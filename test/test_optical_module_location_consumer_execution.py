"""Execution-level tests for the consumer-model Optical Module Location pattern.

These tests are database-backed: they run the *consumer's* workflows end to end through
the real orchestrator-core process engine. The consumer is a subscription model that
has-a the shipped ``OpticalModuleLocationBlock`` under its own attributes
(``router.for_the_optical_module``, reusing the consumer classes of
``test_optical_module_location_composition``), with:

- its own construct step (``from_product_id`` on the consumer model, the block put in
  the state under the shipped ``OPTICAL_MODULE_BLOCK_STATE_KEY``);
- the shipped form generators, used as-is for create/terminate and, for modify, a thin
  consumer wrapper that delegates to the shipped generator with the consumer model and
  attribute (``functools.partial`` pre-binding does not work: the core form-argument
  injection passes the bound parameters positionally from their defaults);
- its own one-step wiring (the consumer's block is not under the shipped
  ``optical_location`` attribute);
- the shipped block step lists and the shipped description step, unchanged.

Together with ``test_optical_module_location_execution.py`` (the as-is shipped product
type) they prove the shipped workflow is only a special case of the consumer pattern:
the same parts execute end to end for a model the module does not know, and the as-is
workflow is the pattern with the construct and wiring steps pre-filled for the
``optical_location`` attribute.
"""

from collections.abc import Callable
from typing import Any
from uuid import uuid4

import pytest
from pydantic_forms.exceptions import FormValidationError
from pydantic_forms.types import FormGenerator, State, UUIDstr
from sqlalchemy import select

import orchestrator.core.db as core_db
from orchestrator.core.db import ProcessStepTable, SubscriptionTable
from orchestrator.core.domain import SUBSCRIPTION_MODEL_REGISTRY, SubscriptionModel
from orchestrator.core.migrations.helpers import create as create_catalog
from orchestrator.core.migrations.helpers import create_workflow as create_workflow_row
from orchestrator.core.targets import Target
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows import LazyWorkflowInstance
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow, modify_workflow, terminate_workflow, validate_workflow
from orchestrator.optical.db import location_block_from_subscription
from orchestrator.optical.products.product_blocks.optical_location import (
    LocationCode,
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_location.create import (
    CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS,
    create_optical_module_location_form_generator,
    populate_optical_module_location_block,
)
from orchestrator.optical.workflows.optical_location.modify import (
    MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS,
    modify_optical_module_location_form_pages,
)
from orchestrator.optical.workflows.optical_location.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    set_optical_module_location_subscription_description,
)
from orchestrator.optical.workflows.optical_location.terminate import (
    OPTICAL_MODULE_LOCATION_TERMINATE_STEPS,
    terminate_initial_input_form_generator,
)
from orchestrator.optical.workflows.optical_location.validate import OPTICAL_MODULE_LOCATION_VALIDATE_STEPS
from orchestrator.optical.workflows.shared import modify_summary_form
from test.test_optical_module_location_composition import (
    AbstractRouter,
    AbstractRouterInactive,
    AbstractRouterProvisioning,
)

pytestmark = pytest.mark.db

CONSUMER_PRODUCT_NAME = "Consumer Router"
CONSUMER_PRODUCT_TYPE = AbstractRouterInactive.__name__
CONSUMER_BLOCK_NAME = "LocationRouterBlock"
CUSTOMER_ID = "cust-1"
SHIPPED_PRODUCT_NAME = "Optical Module Location"

#: The consumer workflows and their targets, seeded into the workflow catalog below.
CONSUMER_WORKFLOWS: dict[str, Target] = {
    "create_consumer_router_location": Target.CREATE,
    "modify_consumer_router_location": Target.MODIFY,
    "validate_consumer_router_location": Target.VALIDATE,
    "terminate_consumer_router_location": Target.TERMINATE,
}


# --- The consumer workflows, composed from the shipped parts ---------------------


@step("Construct Consumer Router subscription model")
def construct_consumer_router_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    longitude: LongitudeCoordinate,
    latitude: LatitudeCoordinate,
    location_code: LocationCode,
    location_name: str | None = None,
) -> State:
    """Construct the PROVISIONING consumer subscription model and put its location block in the state.

    The consumer counterpart of the shipped construct step: the model is built via
    ``from_product_id`` on the consumer's abstract model, the block it composes
    (``router.for_the_optical_module``) is populated with the create-form values
    (the mandatory fields of the PROVISIONING lifecycle) and the subscription is
    transitioned to PROVISIONING in memory, so the block found in the state under
    the shipped ``OPTICAL_MODULE_BLOCK_STATE_KEY`` is the PROVISIONING variant with
    its mandatory fields already set.
    """
    subscription = AbstractRouterInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )
    populate_optical_module_location_block(
        optical_module_block=subscription.router.for_the_optical_module,
        longitude=longitude,
        latitude=latitude,
        location_code=location_code,
        location_name=location_name,
    )
    subscription = AbstractRouterProvisioning.from_other_lifecycle(subscription, SubscriptionLifecycle.PROVISIONING)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_MODULE_BLOCK_STATE_KEY: subscription.router.for_the_optical_module,
    }


@create_workflow(initial_input_form=create_optical_module_location_form_generator)
def create_consumer_router_location() -> StepList:
    """Consumer create workflow: the shipped composition with the consumer construct step."""
    return (
        begin
        >> construct_consumer_router_subscription
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS
        >> set_optical_module_location_subscription_description
        >> store_process_subscription()
    )


@step("Load Consumer Router location block")
def load_consumer_router_location_block(subscription: SubscriptionModel) -> State:
    """Put the consumer's location block in the state under the shipped state key.

    The consumer wiring step: the consumer model composes the block under
    ``router.for_the_optical_module``, not the shipped ``optical_location``
    attribute, so the shipped ``load_optical_module_location_block`` cannot be reused.
    """
    location = getattr(subscription, "router", None)
    if location is None:
        msg = "Consumer Router subscription has no Optical Module Location block under attribute 'router'"
        raise ValueError(msg)
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: location.for_the_optical_module}


def modify_consumer_router_location_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    """The consumer modify form generator, composed from the shipped parts.

    The consumer model composes the block under ``router.for_the_optical_module``
    (under a consumer product block), so the shipped attribute lookup cannot reach
    it: the consumer loads the block and passes it explicitly to the shipped page
    sequence and the summary form. (The core form-argument injection builds the
    generator arguments by name from the workflow state, so the shipped generator's
    ``subscription_model``/``block_field_name`` parameters cannot be pre-bound with
    ``functools.partial`` either: the bound parameters would be passed positionally
    from their signature defaults and collide with the binding.)
    """
    subscription = AbstractRouter.from_subscription(subscription_id)
    location = subscription.router.for_the_optical_module

    user_input_dict = yield from customer_choice_form_page(include=str(subscription.customer_id))
    user_input_dict.update((yield from modify_optical_module_location_form_pages(subscription, location=location)))
    yield from modify_summary_form(
        user_input_dict,
        location,
        ["customer_id", "longitude", "latitude", "location_code", "location_name"],
        extra_before={"customer_id": str(subscription.customer_id)},
    )

    return user_input_dict | {"subscription": subscription}


@modify_workflow(initial_input_form=modify_consumer_router_location_form_generator)
def modify_consumer_router_location() -> StepList:
    """Consumer modify workflow: the shipped composition with the consumer wiring step."""
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_consumer_router_location_block
        >> MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


@validate_workflow()
def validate_consumer_router_location() -> StepList:
    """Consumer validate workflow: the block is validated from the state (the consumer's only option)."""
    return begin >> load_consumer_router_location_block >> OPTICAL_MODULE_LOCATION_VALIDATE_STEPS


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_consumer_router_location() -> StepList:
    """Consumer terminate workflow: the shipped form and steps, unchanged."""
    return begin >> OPTICAL_MODULE_LOCATION_TERMINATE_STEPS


# --- Consumer catalog and workflow registration ----------------------------------


@pytest.fixture(scope="session")
def consumer_router_catalog(postgres_database: Any) -> None:
    """Register the consumer model and seed its catalog rows and workflows.

    Runs after the shipped catalog is provisioned (and drift-verified), so the drift
    gate and the shipped-catalog generation stay shipped-model-only. The seeded rows
    survive the per-test ``TRUNCATE`` of the volatile tables: the catalog tables are
    not truncated.
    """
    SUBSCRIPTION_MODEL_REGISTRY[CONSUMER_PRODUCT_NAME] = AbstractRouterInactive

    with core_db.db.engine.begin() as conn:
        create_catalog(
            conn,
            {
                "products": {
                    CONSUMER_PRODUCT_NAME: {
                        "product_id": str(uuid4()),
                        "product_type": CONSUMER_PRODUCT_TYPE,
                        "description": CONSUMER_PRODUCT_NAME,
                        "tag": "consumer-router",
                        "status": "active",
                        "product_blocks": [CONSUMER_BLOCK_NAME],
                    },
                },
                "product_blocks": {
                    CONSUMER_BLOCK_NAME: {
                        "product_block_id": str(uuid4()),
                        "description": "Consumer-style block composing the shipped Optical Module Location block.",
                        "tag": "location-router",
                        "status": "active",
                        "depends_on_block_relations": ["OpticalModuleLocationBlock"],
                    },
                },
            },
        )
        for name, target in CONSUMER_WORKFLOWS.items():
            create_workflow_row(
                conn,
                {
                    "name": name,
                    "target": target.name,
                    "description": name,
                    "product_type": CONSUMER_PRODUCT_TYPE,
                },
            )

    for name in CONSUMER_WORKFLOWS:
        LazyWorkflowInstance(__name__, name)


# --- Test helpers ----------------------------------------------------------------


def _consumer_create_inputs(product_id_for: Callable[[str], str], location_code: str, location_name: str) -> list[dict]:
    return [
        {"product": product_id_for(CONSUMER_PRODUCT_NAME)},
        {"customer_id": CUSTOMER_ID},
        {"location_code": location_code, "location_name": location_name},
        {"longitude": "12.4964", "latitude": "41.9028"},
        {},
    ]


def _shipped_create_inputs(product_id_for: Callable[[str], str], location_code: str, location_name: str) -> list[dict]:
    return [
        {"product": product_id_for(SHIPPED_PRODUCT_NAME)},
        {"customer_id": CUSTOMER_ID},
        {"location_code": location_code, "location_name": location_name},
        {"longitude": "12.4964", "latitude": "41.9028"},
        {},
    ]


def _run_consumer_create(
    run_process, product_id_for, assert_process_completed, subscription_id_of_process
) -> tuple[str, str]:
    """Run the consumer create workflow and return the (process id, subscription id) pair."""
    inputs = _consumer_create_inputs(product_id_for, "rom-01", "Rome")
    process_id = run_process("create_consumer_router_location", inputs)
    assert_process_completed(process_id)
    return process_id, subscription_id_of_process(process_id)


def _run_shipped_create(run_process, product_id_for, assert_process_completed, subscription_id_of_process) -> str:
    """Run the shipped create workflow and return the subscription id."""
    inputs = _shipped_create_inputs(product_id_for, "dup-01", "Duplicate")
    process_id = run_process("create_optical_module_location", inputs)
    assert_process_completed(process_id)
    return subscription_id_of_process(process_id)


def _subscription_table(subscription_id: str) -> SubscriptionTable:
    with core_db.db.database_scope():
        subscription = core_db.db.session.get(SubscriptionTable, subscription_id)
        assert subscription is not None
        return subscription


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
            step.state[OPTICAL_MODULE_BLOCK_STATE_KEY]
            for step in core_db.db.session.scalars(
                select(ProcessStepTable).where(ProcessStepTable.process_id == process_id)
            )
            if isinstance(step.state, dict) and isinstance(step.state.get(OPTICAL_MODULE_BLOCK_STATE_KEY), dict)
        ]
    assert any(all(block_state.get(key) == value for key, value in expected.items()) for block_state in block_states), (
        "no step state held the round-tripped block with the create form values"
    )


# --- Tests -------------------------------------------------------------------------


def test_consumer_create_end_to_end(
    consumer_router_catalog: None,
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
) -> None:
    """The consumer create workflow executes end to end: model construction, block save, description, relation."""
    process_id, subscription_id = _run_consumer_create(
        run_process, product_id_for, assert_process_completed, subscription_id_of_process
    )

    subscription = _subscription_table(subscription_id)
    assert SubscriptionLifecycle(subscription.status) == SubscriptionLifecycle.ACTIVE
    assert subscription.description == "Rome (rom-01)"
    assert subscription.customer_id == CUSTOMER_ID

    # The block-based (model-agnostic) resolver finds the block of the consumer subscription.
    block = location_block_from_subscription(subscription_id)
    assert isinstance(block, OpticalModuleLocationBlock)
    assert block.location_code == "rom-01"
    assert block.location_name == "Rome"
    assert block.longitude == "12.4964"
    assert block.latitude == "41.9028"

    # The consumer model reloads with the block populated under its own attribute.
    loaded = AbstractRouter.from_subscription(subscription_id)
    assert isinstance(loaded, AbstractRouter)
    assert isinstance(loaded.router.for_the_optical_module, OpticalModuleLocationBlock)
    assert loaded.router.for_the_optical_module.location_code == "rom-01"

    _assert_block_state_round_tripped(process_id)


def test_consumer_full_lifecycle_create_modify_terminate_validate(
    consumer_router_catalog: None,
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
) -> None:
    """The full create -> modify -> validate -> terminate cycle of the consumer workflows."""
    _, subscription_id = _run_consumer_create(
        run_process, product_id_for, assert_process_completed, subscription_id_of_process
    )

    modify_process_id = run_process(
        "modify_consumer_router_location",
        [
            {"subscription_id": subscription_id},
            {"customer_id": CUSTOMER_ID},
            {
                "longitude": "4.9041",
                "latitude": "52.3676",
                "location_code": "ams-01",
                "location_name": "Amsterdam",
                "clear_location_name": False,
            },
            {},
        ],
    )
    assert_process_completed(modify_process_id)
    # The shipped modify steps update the block and the lifecycle but do not refresh
    # the subscription description (only the create workflow does): the description is unchanged.
    assert _subscription_table(subscription_id).description == "Rome (rom-01)"
    block = location_block_from_subscription(subscription_id)
    assert isinstance(block, OpticalModuleLocationBlock)
    assert block.location_code == "ams-01"
    assert block.location_name == "Amsterdam"
    assert block.longitude == "4.9041"
    assert block.latitude == "52.3676"
    assert _subscription_table(subscription_id).insync is True

    # The consumer model still reloads with the updated block under its own attribute.
    loaded = AbstractRouter.from_subscription(subscription_id)
    assert loaded.router.for_the_optical_module.location_code == "ams-01"

    validate_process_id = run_process("validate_consumer_router_location", [{"subscription_id": subscription_id}])
    assert_process_completed(validate_process_id)

    terminate_process_id = run_process(
        "terminate_consumer_router_location",
        [{"subscription_id": subscription_id}, {"subscription_id": subscription_id}],
    )
    assert_process_completed(terminate_process_id)
    assert SubscriptionLifecycle(_subscription_table(subscription_id).status) == SubscriptionLifecycle.TERMINATED
    assert subscription_id_of_process(terminate_process_id) == subscription_id


def test_consumer_subscription_lifecycle_variants_resolve_on_reload(
    consumer_router_catalog: None,
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
    set_subscription_status,
) -> None:
    """INITIAL, PROVISIONING and ACTIVE consumer rows reload as their matching lifecycle variants."""
    _, subscription_id = _run_consumer_create(
        run_process, product_id_for, assert_process_completed, subscription_id_of_process
    )

    active_subscription = AbstractRouter.from_subscription(subscription_id)
    assert isinstance(active_subscription, AbstractRouter)
    assert isinstance(active_subscription.router.for_the_optical_module, OpticalModuleLocationBlock)

    set_subscription_status(subscription_id, SubscriptionLifecycle.PROVISIONING)
    provisioning_subscription = AbstractRouterProvisioning.from_subscription(subscription_id)
    assert isinstance(provisioning_subscription, AbstractRouterProvisioning)
    assert isinstance(provisioning_subscription.router.for_the_optical_module, OpticalModuleLocationBlockProvisioning)

    set_subscription_status(subscription_id, SubscriptionLifecycle.INITIAL)
    inactive_subscription = AbstractRouterInactive.from_subscription(subscription_id)
    assert isinstance(inactive_subscription, AbstractRouterInactive)
    assert isinstance(inactive_subscription.router.for_the_optical_module, OpticalModuleLocationBlockInactive)


def test_consumer_create_rejects_code_used_by_shipped_location(
    consumer_router_catalog: None,
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
) -> None:
    """A consumer create with a location code in use by a SHIPPED location fails the form validation.

    The uniqueness check is block-based, so a shipped product type conflicts with the
    consumer product type for the same code.
    """
    shipped_subscription_id = _run_shipped_create(
        run_process, product_id_for, assert_process_completed, subscription_id_of_process
    )

    with pytest.raises(FormValidationError, match="already in use") as exc_info:
        run_process(
            "create_consumer_router_location",
            _consumer_create_inputs(product_id_for, "dup-01", "Duplicate"),
        )
    assert shipped_subscription_id in str(exc_info.value)
    assert "Duplicate (dup-01)" in str(exc_info.value)


def test_shipped_create_rejects_code_used_by_consumer_location(
    consumer_router_catalog: None,
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
) -> None:
    """A shipped create with a location code in use by a CONSUMER location fails the form validation.

    The reverse direction of the conflict: the check covers composed product types
    without hardcoding a product type.
    """
    _, consumer_subscription_id = _run_consumer_create(
        run_process, product_id_for, assert_process_completed, subscription_id_of_process
    )
    # Re-point the consumer location at the code the shipped create will try to use.
    process_id = run_process(
        "modify_consumer_router_location",
        [
            {"subscription_id": consumer_subscription_id},
            {"customer_id": CUSTOMER_ID},
            {
                "longitude": "12.4964",
                "latitude": "41.9028",
                "location_code": "dup-01",
                "location_name": "Duplicate",
                "clear_location_name": False,
            },
            {},
        ],
    )
    assert_process_completed(process_id)

    with pytest.raises(FormValidationError, match="already in use") as exc_info:
        run_process("create_optical_module_location", _shipped_create_inputs(product_id_for, "dup-01", "Duplicate"))
    assert consumer_subscription_id in str(exc_info.value)


def test_consumer_modify_keeps_own_location_code(
    consumer_router_catalog: None,
    run_process,
    product_id_for,
    assert_process_completed,
    subscription_id_of_process,
) -> None:
    """The modify uniqueness check excludes the consumer subscription being modified."""
    _, subscription_id = _run_consumer_create(
        run_process, product_id_for, assert_process_completed, subscription_id_of_process
    )

    process_id = run_process(
        "modify_consumer_router_location",
        [
            {"subscription_id": subscription_id},
            {"customer_id": CUSTOMER_ID},
            {
                "longitude": "12.4964",
                "latitude": "41.9028",
                "location_code": "rom-01",
                "location_name": "Rome",
                "clear_location_name": False,
            },
            {},
        ],
    )
    assert_process_completed(process_id)
