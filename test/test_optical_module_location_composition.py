"""Composition contract tests for the Optical Module Location workflow parts.

These tests are database-free: they verify the composition contract itself
(class definition, lifecycle pairing, the state key contract of the shipped
block steps and the block population/update logic), not the workflow
execution.
"""

import inspect
import uuid
from functools import partial
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import pytest
from pydantic_forms.validators import Choice

from orchestrator.core.domain.base import ProductBlockModel, SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.utils.json import json_dumps, json_loads
from orchestrator.core.workflow import Workflow, begin
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow, modify_workflow, terminate_workflow, validate_workflow
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.workflows import customer as customer_parts
from orchestrator.optical.workflows.optical_location import create as location_create
from orchestrator.optical.workflows.optical_location import modify as location_modify
from orchestrator.optical.workflows.optical_location import shared as location_shared
from orchestrator.optical.workflows.optical_location import terminate as location_terminate
from orchestrator.optical.workflows.optical_location import validate as location_validate
from orchestrator.optical.workflows.optical_location.create import (
    CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS,
    construct_optical_module_location_subscription,
    create_optical_module_location_form_generator,
    populate_optical_module_location_block,
)
from orchestrator.optical.workflows.optical_location.modify import (
    MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS,
    modify_optical_module_location_form_generator,
    update_optical_module_location_block,
)
from orchestrator.optical.workflows.optical_location.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    load_optical_module_location_block,
    optical_location_block_from_state,
    optical_module_location_subscription_description,
    save_optical_module_location_block,
    set_optical_module_location_subscription_description,
)
from orchestrator.optical.workflows.optical_location.terminate import (
    OPTICAL_MODULE_LOCATION_TERMINATE_STEPS,
)
from orchestrator.optical.workflows.optical_location.terminate import (
    terminate_initial_input_form_generator as location_terminate_initial_input_form_generator,
)
from orchestrator.optical.workflows.optical_location.validate import (
    OPTICAL_MODULE_LOCATION_VALIDATE_STEPS,
    validate_optical_module_location_block,
    validate_optical_module_location_block_step,
)


class RouterBlockInactive(ProductBlockModel, product_block_name="LocationRouterBlock"):
    """Consumer-style product block with a has-a relation to the shipped location block."""

    for_the_optical_module: OpticalModuleLocationBlockInactive


class RouterBlockProvisioning(RouterBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """The provisioning variant of the consumer-style block."""

    for_the_optical_module: OpticalModuleLocationBlockProvisioning


class RouterBlock(RouterBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style block."""

    for_the_optical_module: OpticalModuleLocationBlock


class _AbstractRouterInactive(SubscriptionModel):
    """Abstract consumer-style subscription model composing the block."""

    router: RouterBlockInactive


class _AbstractRouterProvisioning(AbstractRouterInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """The provisioning variant of the consumer-style subscription model."""

    router: RouterBlockProvisioning


class _AbstractRouter(AbstractRouterProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style subscription model."""

    router: RouterBlock


BASE_BLOCK_FIELDS = {"name", "label", "subscription_instance_id", "owner_subscription_id"}


def _make_location_block() -> OpticalModuleLocationBlockInactive:
    return OpticalModuleLocationBlockInactive(
        name="OpticalModuleLocationBlock",
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=uuid.uuid4(),
    )


def _make_location_block_provisioning() -> OpticalModuleLocationBlockProvisioning:
    return OpticalModuleLocationBlockProvisioning.model_construct(
        name="OpticalModuleLocationBlock",
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=uuid.uuid4(),
        longitude="12.4964",
        latitude="41.9028",
        location_code="rom-01",
    )


@pytest.fixture(autouse=True)
def _mock_location_code_uniqueness_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """DB-free: the uniqueness check never queries the database in the composition tests.

    Tests exercising the check itself re-patch the helper with a fake.
    """
    monkeypatch.setattr(location_create, "check_location_code_uniqueness", Mock(return_value=None))
    monkeypatch.setattr(location_modify, "check_location_code_uniqueness", Mock(return_value=None))


def _step_functions(steps):
    return [cast(Any, step).__wrapped__ for step in steps]


@pytest.mark.parametrize(
    ("chain_class", "expected_field_type"),
    [
        (RouterBlockInactive, OpticalModuleLocationBlockInactive),
        (RouterBlockProvisioning, OpticalModuleLocationBlockProvisioning),
        (RouterBlock, OpticalModuleLocationBlock),
    ],
)
def test_composed_block_is_classified_as_product_block_field(chain_class, expected_field_type) -> None:
    assert chain_class._product_block_fields_ == {"for_the_optical_module": expected_field_type}
    assert "for_the_optical_module" not in chain_class._non_product_block_fields_


@pytest.mark.parametrize("chain_class", [RouterBlockInactive, RouterBlockProvisioning, RouterBlock])
def test_composed_block_redeclares_every_inherited_field(chain_class) -> None:
    annotations = inspect.get_annotations(chain_class)
    assert set(chain_class.model_fields) - BASE_BLOCK_FIELDS <= set(annotations)


@pytest.mark.parametrize(
    ("chain_class", "expected_field_type"),
    [
        (AbstractRouterInactive, RouterBlockInactive),
        (AbstractRouterProvisioning, RouterBlockProvisioning),
        (AbstractRouter, RouterBlock),
    ],
)
def test_composed_subscription_model_is_classified(chain_class, expected_field_type) -> None:
    assert chain_class._product_block_fields_ == {"router": expected_field_type}


def test_populate_optical_module_location_block() -> None:
    block = _make_location_block()

    populate_optical_module_location_block(
        optical_module_block=block,
        longitude="12.4964",
        latitude="41.9028",
        location_code="rom-01",
        location_name="Rome",
    )

    assert block.longitude == "12.4964"
    assert block.latitude == "41.9028"
    assert block.location_code == "rom-01"
    assert block.location_name == "Rome"


def test_update_optical_module_location_block(monkeypatch) -> None:
    block = _make_location_block()
    monkeypatch.setattr(location_modify, "optical_location_block_from_state", Mock(return_value=block))

    cast(Any, update_optical_module_location_block).__wrapped__(
        optical_module_block=block,
        longitude="4.9041",
        latitude="52.3676",
        location_code="ams-01",
        location_name="Amsterdam",
        clear_location_name=False,
    )

    assert block.longitude == "4.9041"
    assert block.latitude == "52.3676"
    assert block.location_code == "ams-01"
    assert block.location_name == "Amsterdam"


def test_update_optical_module_location_block_can_clear_optional_fields(monkeypatch) -> None:
    block = _make_location_block()
    block.location_name = "Amsterdam"
    monkeypatch.setattr(location_modify, "optical_location_block_from_state", Mock(return_value=block))

    cast(Any, update_optical_module_location_block).__wrapped__(
        optical_module_block=block,
        longitude="4.9041",
        latitude="52.3676",
        location_code="ams-01",
        location_name="Amsterdam",
        clear_location_name=True,
    )

    assert block.location_name is None


def test_block_steps_consume_the_block_state_key() -> None:
    for step_func in _step_functions(CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS):
        signature = inspect.signature(step_func)
        assert OPTICAL_MODULE_BLOCK_STATE_KEY in signature.parameters


def test_location_block_state_key_matches_the_documented_contract() -> None:
    """The state key literal matches the value documented in the README state-contract table."""
    assert OPTICAL_MODULE_BLOCK_STATE_KEY == "optical_module_block"


def test_block_steps_take_the_lifecycle_matching_block_variant() -> None:
    """Every shipped block step operates on the PROVISIONING variant of the block."""
    save = cast(Any, next(step for step in CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS)).__wrapped__
    update = cast(Any, next(step for step in MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS)).__wrapped__

    assert inspect.signature(save).parameters[OPTICAL_MODULE_BLOCK_STATE_KEY].annotation is (
        OpticalModuleLocationBlockProvisioning
    )
    assert inspect.signature(update).parameters[OPTICAL_MODULE_BLOCK_STATE_KEY].annotation is (
        OpticalModuleLocationBlockProvisioning
    )


def test_optical_location_block_from_state_rehydrates_a_round_tripped_block(monkeypatch) -> None:
    """Workflow steps execute with the state serialized between steps: the block arrives as a dict."""
    block = _make_location_block_provisioning()

    def fake_from_state(block_dict):
        assert block_dict["subscription_instance_id"] == str(block.subscription_instance_id)
        return block

    monkeypatch.setattr(location_shared, "_optical_module_location_block_from_state", fake_from_state)

    with pytest.raises(ValueError, match="No Optical Module Location block in the state"):
        optical_location_block_from_state(None)
    assert optical_location_block_from_state(block) is block

    round_tripped = cast(Any, json_loads(json_dumps({OPTICAL_MODULE_BLOCK_STATE_KEY: block})))
    assert isinstance(round_tripped[OPTICAL_MODULE_BLOCK_STATE_KEY], dict)
    assert optical_location_block_from_state(round_tripped[OPTICAL_MODULE_BLOCK_STATE_KEY]) is block


def test_optical_location_block_from_state_rejects_dict_without_subscription_instance_id() -> None:
    """A serialized block without a ``subscription_instance_id`` cannot be re-hydrated."""
    with pytest.raises(ValueError, match="subscription_instance_id"):
        optical_location_block_from_state({})


def test_optical_location_block_from_state_rejects_unknown_subscription_instance_id(monkeypatch) -> None:
    """An unknown ``subscription_instance_id`` cannot be re-hydrated (no such instance)."""
    fake_session = Mock()
    fake_session.get.return_value = None
    monkeypatch.setattr(location_shared, "db", SimpleNamespace(session=fake_session))

    with pytest.raises(ValueError, match="No subscription instance"):
        optical_location_block_from_state({"subscription_instance_id": str(uuid.uuid4())})


def test_save_block_step_fails_fast_when_state_has_no_block() -> None:
    """The save step fails fast when the state holds no Optical Module Location block."""
    subscription = cast(Any, SimpleNamespace(subscription_id=uuid.uuid4(), status=SubscriptionLifecycle.PROVISIONING))
    with pytest.raises(ValueError, match="No Optical Module Location block in the state"):
        cast(Any, save_optical_module_location_block).__wrapped__(
            subscription=subscription,
            optical_module_block=None,
        )


def test_update_block_step_fails_fast_when_state_has_no_block() -> None:
    """The update step fails fast when the state holds no Optical Module Location block."""
    with pytest.raises(ValueError, match="No Optical Module Location block in the state"):
        cast(Any, update_optical_module_location_block).__wrapped__(
            optical_module_block=None,
            longitude="4.9041",
            latitude="52.3676",
            location_code="ams-01",
            location_name="Amsterdam",
            clear_location_name=False,
        )


def _make_conflicting_location_instance(
    description: str | None = None,
    subscription_id: uuid.UUID | None = None,
) -> SimpleNamespace:
    """Return a fake subscription instance row for the uniqueness query helper."""
    return SimpleNamespace(
        subscription_id=subscription_id or uuid.uuid4(),
        subscription=None if description is None else SimpleNamespace(description=description),
    )


def test_check_location_code_uniqueness_passes_when_unused(monkeypatch) -> None:
    monkeypatch.setattr(
        location_shared, "subscription_instances_by_block_type_and_resource_value", Mock(return_value=[])
    )

    location_shared.check_location_code_uniqueness("rom-01")


def test_check_location_code_uniqueness_raises_on_conflict(monkeypatch) -> None:
    conflicting = _make_conflicting_location_instance(description="Rome (rom-01)")
    monkeypatch.setattr(
        location_shared,
        "subscription_instances_by_block_type_and_resource_value",
        Mock(return_value=[conflicting]),
    )

    with pytest.raises(ValueError, match="already in use") as exc_info:
        location_shared.check_location_code_uniqueness("rom-01")

    assert str(conflicting.subscription_id) in str(exc_info.value)
    assert "Rome (rom-01)" in str(exc_info.value)


def test_check_location_code_uniqueness_ignores_only_the_excluded_subscription(monkeypatch) -> None:
    excluded = uuid.uuid4()
    excluded_instance = _make_conflicting_location_instance(description="Rome (rom-01)", subscription_id=excluded)
    other = _make_conflicting_location_instance(description="Amsterdam (ams-01)")
    monkeypatch.setattr(
        location_shared,
        "subscription_instances_by_block_type_and_resource_value",
        Mock(return_value=[excluded_instance, other]),
    )

    with pytest.raises(ValueError, match=r"Amsterdam \(ams-01\)"):
        location_shared.check_location_code_uniqueness("rom-01", exclude_subscription_id=str(excluded))


def test_create_identity_form_rejects_duplicate_location_code(monkeypatch) -> None:
    def fake_check(location_code, exclude_subscription_id=None):
        assert exclude_subscription_id is None
        msg = f"Location code '{location_code}' is already in use by subscription {uuid.uuid4()}"
        raise ValueError(msg)

    monkeypatch.setattr(location_create, "check_location_code_uniqueness", fake_check)
    page = cast(Any, location_create.create_optical_module_location_identity_form("Optical Module Location"))

    with pytest.raises(ValueError, match="already in use"):
        page(location_code="rom-01", location_name="Rome")


def test_modify_form_rejects_duplicate_location_code_excluding_self(monkeypatch) -> None:
    block = _make_location_block()
    block.longitude = "4.9041"
    block.latitude = "52.3676"
    block.location_code = "ams-01"
    block.location_name = "Amsterdam"
    subscription = cast(
        Any,
        SimpleNamespace(customer_id="cust-1", subscription_id=uuid.uuid4(), optical_location=block),
    )

    def fake_check(location_code, exclude_subscription_id=None):
        assert exclude_subscription_id == str(subscription.subscription_id)
        msg = f"Location code '{location_code}' is already in use by subscription {uuid.uuid4()}"
        raise ValueError(msg)

    monkeypatch.setattr(location_modify, "check_location_code_uniqueness", fake_check)
    page = cast(Any, location_modify.modify_optical_module_location_form(subscription))

    with pytest.raises(ValueError, match="already in use"):
        page(
            longitude="4.9041",
            latitude="52.3676",
            location_code="ams-01",
            location_name="Amsterdam",
        )


def test_populate_block_rejects_duplicate_location_code(monkeypatch) -> None:
    block = _make_location_block()

    def fake_check(location_code, exclude_subscription_id=None):
        assert exclude_subscription_id == str(block.owner_subscription_id)
        msg = f"Location code '{location_code}' is already in use by subscription {uuid.uuid4()}"
        raise ValueError(msg)

    monkeypatch.setattr(location_create, "check_location_code_uniqueness", fake_check)

    with pytest.raises(ValueError, match="already in use"):
        populate_optical_module_location_block(
            optical_module_block=block,
            longitude="12.4964",
            latitude="41.9028",
            location_code="rom-01",
            location_name="Rome",
        )

    assert block.location_code is None


def test_update_block_rejects_duplicate_location_code_excluding_self(monkeypatch) -> None:
    block = _make_location_block()

    def fake_check(location_code, exclude_subscription_id=None):
        assert exclude_subscription_id == str(block.owner_subscription_id)
        msg = f"Location code '{location_code}' is already in use by subscription {uuid.uuid4()}"
        raise ValueError(msg)

    monkeypatch.setattr(location_modify, "check_location_code_uniqueness", fake_check)
    monkeypatch.setattr(location_modify, "optical_location_block_from_state", Mock(return_value=block))

    with pytest.raises(ValueError, match="already in use"):
        cast(Any, update_optical_module_location_block).__wrapped__(
            optical_module_block=block,
            longitude="4.9041",
            latitude="52.3676",
            location_code="ams-01",
            location_name="Amsterdam",
            clear_location_name=False,
        )

    assert block.location_code is None


def test_set_optical_module_location_subscription_description(monkeypatch) -> None:
    block = _make_location_block()
    block.location_code = "rom-01"
    block.location_name = "Rome"
    subscription = cast(Any, SimpleNamespace(description=""))
    monkeypatch.setattr(location_shared, "optical_location_block_from_state", Mock(return_value=block))

    state = cast(Any, set_optical_module_location_subscription_description).__wrapped__(
        subscription=subscription, optical_module_block=block
    )

    assert subscription.description == "Rome (rom-01)"
    assert state["subscription_description"] == "Rome (rom-01)"


def test_shipped_type_create_workflow_composition() -> None:
    @create_workflow(
        initial_input_form=partial(
            create_optical_module_location_form_generator, product_name="Optical Module Location"
        )
    )
    def create_optical_module_location():
        return (
            begin
            >> construct_optical_module_location_subscription
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS
            >> set_optical_module_location_subscription_description
            >> store_process_subscription()
        )

    workflow: Workflow = create_optical_module_location
    assert workflow.name == "create_optical_module_location"
    names = [step.name for step in workflow.steps]
    assert names.index("Construct Subscription model") < names.index("Set subscription to 'provisioning'")
    assert names.index("Set subscription to 'provisioning'") < names.index("Persist optical module location block")
    assert names.index("Persist optical module location block") < names.index(
        "Set Optical Module Location subscription description"
    )
    assert names.index("Set Optical Module Location subscription description") < names.index(
        "Create Process Subscription relation"
    )


def _fake_customer_choice(include: str | None = None) -> type[Choice]:
    return cast(type[Choice], Choice.__call__("FakeCustomerChoice", {"cust-1": "cust-1", "cust-2": "cust-2"}))


def _finish_form(generator, page_instance: FormPage) -> dict[str, Any]:
    """Send the last user input and return the return value of the form generator."""
    with pytest.raises(StopIteration) as exc_info:
        generator.send(page_instance)
    return exc_info.value.value


def test_create_form_pages_yield_the_shipped_pages_in_order() -> None:
    generator = location_create.create_optical_module_location_form_pages("Optical Module Location")

    page_1 = next(generator)
    assert issubclass(page_1, FormPage)
    assert set(page_1.model_fields) == {"location_code", "location_name"}

    page_2 = generator.send(page_1(location_code="rom-01", location_name="Rome"))
    assert issubclass(page_2, FormPage)
    assert set(page_2.model_fields) == {"longitude", "latitude"}

    user_input = _finish_form(generator, page_2(longitude="12.4964", latitude="41.9028"))
    assert user_input == {
        "longitude": "12.4964",
        "latitude": "41.9028",
        "location_code": "rom-01",
        "location_name": "Rome",
    }


def test_customer_choice_form_pages_yield_the_customer_page(monkeypatch) -> None:
    monkeypatch.setattr(customer_parts, "customer_choice_selector", _fake_customer_choice)

    generator = customer_parts.customer_choice_form_page()
    page = next(generator)
    assert issubclass(page, FormPage)
    assert set(page.model_fields) == {"customer_id"}

    user_input = _finish_form(generator, page(customer_id="cust-1"))
    assert user_input == {"customer_id": "cust-1"}


def test_create_form_pages_compose_in_one_line_in_consumer_space(monkeypatch) -> None:
    monkeypatch.setattr(customer_parts, "customer_choice_selector", _fake_customer_choice)

    def my_create_form_generator(product_name):
        user_input_dict = yield from customer_parts.customer_choice_form_page()
        user_input_dict.update((yield from location_create.create_optical_module_location_form_pages(product_name)))
        return user_input_dict

    generator = my_create_form_generator("Optical Module Location")
    customer_page = next(generator)
    page_1 = generator.send(customer_page(customer_id="cust-1"))
    page_2 = generator.send(page_1(location_code="rom-01", location_name="Rome"))
    user_input = _finish_form(generator, page_2(longitude="12.4964", latitude="41.9028"))

    assert user_input["customer_id"] == "cust-1"
    assert user_input["location_code"] == "rom-01"
    assert user_input["location_name"] == "Rome"


def test_modify_form_pages_yield_the_prefilled_page() -> None:
    block = _make_location_block()
    block.longitude = "4.9041"
    block.latitude = "52.3676"
    block.location_code = "ams-01"
    block.location_name = "Amsterdam"
    subscription = cast(
        Any,
        SimpleNamespace(customer_id="cust-1", subscription_id=uuid.uuid4(), optical_location=block),
    )

    generator = location_modify.modify_optical_module_location_form_pages(subscription)
    page = next(generator)
    assert issubclass(page, FormPage)
    assert page.model_fields["longitude"].default == "4.9041"
    assert page.model_fields["latitude"].default == "52.3676"
    assert page.model_fields["location_code"].default == "ams-01"
    assert page.model_fields["location_name"].default == "Amsterdam"
    assert "clear_location_name" in page.model_fields

    user_input = _finish_form(
        generator,
        page(
            longitude="4.9041",
            latitude="52.3676",
            location_code="ams-01",
            location_name="Amsterdam",
        ),
    )
    assert user_input["location_code"] == "ams-01"
    assert user_input["clear_location_name"] is False


def test_terminate_form_pages_yield_the_confirmation_page() -> None:
    subscription_id = str(uuid.uuid4())

    generator = location_terminate.terminate_optical_module_location_form_pages(subscription_id)
    page = next(generator)
    assert issubclass(page, FormPage)
    assert set(page.model_fields) == {"subscription_id"}
    assert page.model_fields["subscription_id"].default == subscription_id


def test_shipped_type_modify_workflow_composition() -> None:
    @modify_workflow(initial_input_form=modify_optical_module_location_form_generator)
    def modify_optical_module_location():
        return (
            begin
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> load_optical_module_location_block
            >> MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS
            >> set_status(SubscriptionLifecycle.ACTIVE)
        )

    workflow: Workflow = modify_optical_module_location
    assert workflow.name == "modify_optical_module_location"
    names = [step.name for step in workflow.steps]
    assert names.index("Load optical module location block") < names.index("Updating Optical Module Location block")
    assert names.index("Updating Optical Module Location block") < names.index("Persist optical module location block")


def test_consumer_model_modify_workflow_composition() -> None:
    # The core form-argument injection builds the generator arguments by name from the
    # workflow state, so the shipped generator's subscription_model/block_field_name
    # parameters cannot be pre-bound with functools.partial (the bound parameters would
    # be passed positionally from their signature defaults). The consumer binds them
    # with a thin wrapper that delegates to the shipped generator as a direct call.
    def my_modify_form_generator(subscription_id):
        user_input_dict = yield from modify_optical_module_location_form_generator(
            subscription_id,
            subscription_model=AbstractRouter,
            block_field_name="router",
        )
        return user_input_dict

    @modify_workflow(initial_input_form=my_modify_form_generator)
    def modify_my_router():
        return begin >> MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS

    workflow: Workflow = modify_my_router
    assert workflow.name == "modify_my_router"
    names = [step.name for step in workflow.steps]
    assert names.index("Updating Optical Module Location block") < names.index("Persist optical module location block")


def test_terminate_and_validate_shared_step_lists_compose() -> None:
    @terminate_workflow(initial_input_form=location_terminate_initial_input_form_generator)
    def terminate_my_location():
        return begin >> OPTICAL_MODULE_LOCATION_TERMINATE_STEPS

    @validate_workflow()
    def validate_my_location():
        return begin >> OPTICAL_MODULE_LOCATION_VALIDATE_STEPS

    assert terminate_my_location.name == "terminate_my_location"
    assert validate_my_location.name == "validate_my_location"
    assert "Deprovision Optical Module Location" in [step.name for step in terminate_my_location.steps]
    assert "Load initial state" in [step.name for step in validate_my_location.steps]


@pytest.mark.parametrize(
    "subscription",
    [
        cast(Any, SimpleNamespace()),
        cast(Any, SimpleNamespace(optical_location=None)),
    ],
)
def test_load_optical_module_location_block_fails_fast_when_subscription_has_no_block(subscription) -> None:
    with pytest.raises(ValueError, match="under attribute 'optical_location'") as exc_info:
        cast(Any, load_optical_module_location_block).__wrapped__(subscription)

    assert "must have-a" in str(exc_info.value)


def test_load_optical_module_location_block_returns_block_in_state() -> None:
    block = _make_location_block()
    subscription = cast(Any, SimpleNamespace(optical_location=block))

    state = cast(Any, load_optical_module_location_block).__wrapped__(subscription)

    assert state == {OPTICAL_MODULE_BLOCK_STATE_KEY: block}


def test_optical_module_location_subscription_description_fails_fast_without_block() -> None:
    subscription = cast(Any, SimpleNamespace())

    with pytest.raises(ValueError, match="must have-a"):
        optical_module_location_subscription_description(subscription)


def test_optical_module_location_subscription_description_takes_the_explicit_block() -> None:
    block = _make_location_block_provisioning()
    block.location_name = "Rome"
    subscription = cast(Any, SimpleNamespace())

    assert optical_module_location_subscription_description(subscription, block) == "Rome (rom-01)"


def test_validate_optical_module_location_state_fails_fast_when_subscription_has_no_block() -> None:
    subscription = cast(Any, SimpleNamespace())

    with pytest.raises(ValueError, match="under attribute 'optical_location'") as exc_info:
        cast(Any, validate_optical_module_location_block_step).__wrapped__(
            subscription=subscription, optical_module_block=None
        )

    assert "must have-a" in str(exc_info.value)
    assert "not fully provisioned" not in str(exc_info.value)


def test_validate_optical_module_location_block_fails_on_unprovisioned_block() -> None:
    block = _make_location_block()

    with pytest.raises(ValueError, match="not fully provisioned"):
        validate_optical_module_location_block(block)


def test_validate_optical_module_location_block_passes_on_provisioned_block() -> None:
    block = _make_location_block()
    block.longitude = "12.4964"
    block.latitude = "41.9028"
    block.location_code = "rom-01"

    assert validate_optical_module_location_block(block) is None


def test_validate_optical_module_location_state_validates_the_block_from_the_state(monkeypatch) -> None:
    block = _make_location_block()
    block.longitude = "12.4964"
    block.latitude = "41.9028"
    block.location_code = "rom-01"
    subscription = cast(Any, SimpleNamespace())
    monkeypatch.setattr(location_validate, "optical_location_block_from_state", Mock(return_value=block))

    state = cast(Any, validate_optical_module_location_block_step).__wrapped__(
        subscription=subscription, optical_module_block=block
    )

    assert state == {}


def test_optical_module_location_subscription_description() -> None:
    from types import SimpleNamespace

    block = _make_location_block()
    subscription = cast(Any, SimpleNamespace(optical_location=block))

    block.location_code = "rom-01"
    block.location_name = "Rome"
    assert optical_module_location_subscription_description(subscription) == "Rome (rom-01)"

    block.location_name = None
    assert optical_module_location_subscription_description(subscription) == "rom-01"
