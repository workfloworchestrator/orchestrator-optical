"""Composition contract tests for the Optical Coherent Pluggable workflow parts.

These tests are database-free: they verify the composition contract itself
(class definition, lifecycle pairing, field classification, the state key
contract of the shipped block steps, the block re-hydration from a
round-tripped state and the block population logic), not the workflow
execution.
"""

import inspect
import uuid
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import pytest
from pydantic_forms.validators import Choice

from orchestrator.core.domain.base import ProductBlockModel, SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.utils.json import json_dumps, json_loads
from orchestrator.core.utils.state import inject_args
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_location import OpticalModuleLocationBlockInactive
from orchestrator.optical.products.product_blocks.optical_node_management import (
    OpticalModuleNodeManagementBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_packet_node import OpticalModulePacketNodeInactive
from orchestrator.optical.products.product_types.optical_coherent_pluggable import OpticalCoherentPluggablePartNumber
from orchestrator.optical.workflows.optical_coherent_pluggable import create as create_parts
from orchestrator.optical.workflows.optical_coherent_pluggable import modify as modify_parts
from orchestrator.optical.workflows.optical_coherent_pluggable import shared as shared_parts
from orchestrator.optical.workflows.optical_coherent_pluggable import terminate as terminate_parts
from orchestrator.optical.workflows.optical_coherent_pluggable.create import (
    CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS,
    populate_optical_coherent_pluggable_block,
    populate_optical_coherent_pluggable_block_step,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.modify import (
    MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS,
    update_optical_coherent_pluggable_block,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.shared import (
    OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY,
    load_optical_coherent_pluggable_block,
    optical_coherent_pluggable_block_from_state,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.terminate import (
    OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.validate import (
    OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS,
    validate_optical_coherent_pluggable_state,
)


class RouterBlockInactive(ProductBlockModel, product_block_name="TestRouterBlock"):
    """Consumer-style product block with a has-a relation to the shipped Coherent Pluggable block."""

    for_the_optical_module: OpticalCoherentPluggableBlockInactive


class RouterBlockProvisioning(RouterBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """The provisioning variant of the consumer-style block."""

    for_the_optical_module: OpticalCoherentPluggableBlockProvisioning


class RouterBlock(RouterBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style block."""

    for_the_optical_module: OpticalCoherentPluggableBlock


class AbstractRouterInactive(SubscriptionModel, is_base=True):
    """Abstract consumer-style subscription model composing the block."""

    router: RouterBlockInactive


class AbstractRouterProvisioning(AbstractRouterInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """The provisioning variant of the consumer-style subscription model."""

    router: RouterBlockProvisioning


class AbstractRouter(AbstractRouterProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style subscription model."""

    router: RouterBlock


BASE_BLOCK_FIELDS = {"name", "label", "subscription_instance_id", "owner_subscription_id"}


def _make_packet_node_block() -> OpticalModulePacketNodeInactive:
    subscription_id = uuid.uuid4()
    return OpticalModulePacketNodeInactive(
        name="OpticalModulePacketNode",
        subscription_instance_id=subscription_id,
        owner_subscription_id=subscription_id,
        management=OpticalModuleNodeManagementBlockInactive(
            name="OpticalModuleNodeManagementBlock",
            subscription_instance_id=uuid.uuid4(),
            owner_subscription_id=subscription_id,
            optical_module_node_fqdn="node.example.com",
        ),
        location=OpticalModuleLocationBlockInactive(
            name="OpticalModuleLocationBlock",
            subscription_instance_id=uuid.uuid4(),
            owner_subscription_id=subscription_id,
        ),
    )


def _make_pluggable_block() -> OpticalCoherentPluggableBlockInactive:
    return OpticalCoherentPluggableBlockInactive(
        name="CoherentPluggableBlock",
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=uuid.uuid4(),
        optical_port_host_node=_make_packet_node_block(),
    )


@pytest.fixture(autouse=True)
def _mock_port_uniqueness_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """DB-free: the port uniqueness check never queries the database in the composition tests.

    Tests exercising the check itself re-patch the helper with a fake.
    """
    monkeypatch.setattr(create_parts, "check_optical_coherent_pluggable_port_uniqueness", Mock(return_value=None))


def _step_functions(steps):
    return [cast(Any, step).__wrapped__ for step in steps]


@pytest.mark.parametrize(
    ("chain_class", "expected_field_type"),
    [
        (RouterBlockInactive, OpticalCoherentPluggableBlockInactive),
        (RouterBlockProvisioning, OpticalCoherentPluggableBlockProvisioning),
        (RouterBlock, OpticalCoherentPluggableBlock),
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


@pytest.mark.parametrize(
    "steps",
    [
        CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS,
        MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS,
        OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS,
        OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS,
    ],
)
def test_shipped_block_step_lists_are_non_empty(steps) -> None:
    assert len(steps) > 0


@pytest.mark.parametrize(
    "steps",
    [CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS, MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS],
)
def test_block_steps_consume_the_block_state_key(steps) -> None:
    for step_func in _step_functions(steps):
        signature = inspect.signature(step_func)
        assert OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY in signature.parameters


def test_shared_step_lists_are_block_agnostic() -> None:
    for step_func in _step_functions(OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS):
        signature = inspect.signature(step_func)
        assert OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY not in signature.parameters
    for step_func in _step_functions(OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS):
        signature = inspect.signature(step_func)
        assert OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY not in signature.parameters or (
            signature.parameters[OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY].default is None
        )


def test_optical_coherent_pluggable_block_state_key_matches_the_documented_contract() -> None:
    """The state key literal matches the value documented in the README state-contract table."""
    assert OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY == "optical_coherent_pluggable_block"


def test_block_steps_take_the_lifecycle_matching_block_variant() -> None:
    populate = cast(Any, next(step for step in CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS)).__wrapped__
    update = cast(Any, next(step for step in MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS)).__wrapped__

    assert inspect.signature(populate).parameters[OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY].annotation is (
        OpticalCoherentPluggableBlockInactive
    )
    assert inspect.signature(update).parameters[OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY].annotation is (
        OpticalCoherentPluggableBlockProvisioning
    )


def test_populate_optical_coherent_pluggable_block() -> None:
    block = _make_pluggable_block()
    host_node = _make_packet_node_block()

    populate_optical_coherent_pluggable_block(
        optical_coherent_pluggable_block=block,
        optical_port_host_node=host_node,
        optical_port_name="port-1",
        optical_port_description="desc",
        optical_coherent_pluggable_firmware_version="1.0",
    )

    assert block.optical_port_host_node is host_node
    assert block.optical_port_name == "port-1"
    assert block.optical_port_description == "desc"
    assert block.optical_coherent_pluggable_firmware_version == "1.0"


def test_populate_block_rejects_duplicate_port(monkeypatch) -> None:
    block = _make_pluggable_block()

    def fake_check(port_name, host_node_block, exclude_subscription_id=None):
        assert exclude_subscription_id == str(block.owner_subscription_id)
        msg = f"Port {port_name} on node is already occupied by subscription {uuid.uuid4()}"
        raise ValueError(msg)

    monkeypatch.setattr(create_parts, "check_optical_coherent_pluggable_port_uniqueness", fake_check)

    with pytest.raises(ValueError, match="already occupied"):
        populate_optical_coherent_pluggable_block(
            optical_coherent_pluggable_block=block,
            optical_port_host_node=_make_packet_node_block(),
            optical_port_name="port-1",
            optical_port_description="desc",
            optical_coherent_pluggable_firmware_version="1.0",
        )

    assert block.optical_port_name is None


def test_populate_block_step_resolves_the_state(monkeypatch) -> None:
    host_node = _make_packet_node_block()
    monkeypatch.setattr(create_parts, "packet_node_block_from_subscription", lambda _id: host_node)
    block = _make_pluggable_block()
    state = {
        OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY: block,
        "optical_packet_node_id": str(uuid.uuid4()),
        "optical_port_name": "port-1",
        "optical_port_description": "desc",
        "optical_coherent_pluggable_firmware_version": "1.0",
    }

    wrapped = inject_args(cast(Any, populate_optical_coherent_pluggable_block_step).__wrapped__)
    result = wrapped(dict(state))

    assert result[OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY] is block
    assert block.optical_port_host_node is host_node
    assert block.optical_port_name == "port-1"
    assert block.optical_port_description == "desc"
    assert block.optical_coherent_pluggable_firmware_version == "1.0"


def test_update_optical_coherent_pluggable_block() -> None:
    block = _make_pluggable_block()

    cast(Any, update_optical_coherent_pluggable_block).__wrapped__(
        optical_coherent_pluggable_block=block,
        optical_port_description="new desc",
        optical_coherent_pluggable_firmware_version="2.0",
    )

    assert block.optical_port_description == "new desc"
    assert block.optical_coherent_pluggable_firmware_version == "2.0"


def test_optical_coherent_pluggable_block_from_state_rehydrates_a_round_tripped_block(monkeypatch) -> None:
    """Workflow steps execute with the state serialized between steps: the block arrives as a dict."""
    block = _make_pluggable_block()

    def fake_from_state(block_dict):
        assert block_dict["subscription_instance_id"] == str(block.subscription_instance_id)
        return block

    monkeypatch.setattr(shared_parts, "_optical_coherent_pluggable_block_from_state", fake_from_state)

    assert optical_coherent_pluggable_block_from_state(None) is None
    assert optical_coherent_pluggable_block_from_state(block) is block

    round_tripped = _round_tripped_block_state(block, monkeypatch)
    assert isinstance(round_tripped[OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY], dict)
    assert (
        optical_coherent_pluggable_block_from_state(round_tripped[OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY]) is block
    )


def test_block_steps_rehydrate_the_block_from_a_round_tripped_state(monkeypatch) -> None:
    """The populate step re-hydrates the block from the database by its subscription_instance_id."""
    block = _make_pluggable_block()

    def fake_from_state(block_dict):
        assert block_dict["subscription_instance_id"] == str(block.subscription_instance_id)
        return block

    monkeypatch.setattr(shared_parts, "_optical_coherent_pluggable_block_from_state", fake_from_state)
    monkeypatch.setattr(create_parts, "packet_node_block_from_subscription", lambda _id: _make_packet_node_block())

    round_tripped = _round_tripped_block_state(block, monkeypatch)
    state = round_tripped | {
        "optical_packet_node_id": str(uuid.uuid4()),
        "optical_port_name": "port-1",
        "optical_port_description": "desc",
        "optical_coherent_pluggable_firmware_version": "1.0",
    }

    wrapped = inject_args(cast(Any, populate_optical_coherent_pluggable_block_step).__wrapped__)
    result = wrapped(dict(state))

    assert result[OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY] is block
    assert block.optical_port_name == "port-1"
    assert block.optical_port_description == "desc"
    assert block.optical_coherent_pluggable_firmware_version == "1.0"


def test_optical_coherent_pluggable_block_from_state_rejects_dict_without_subscription_instance_id() -> None:
    """A serialized block without a ``subscription_instance_id`` cannot be re-hydrated."""
    with pytest.raises(ValueError, match="subscription_instance_id"):
        optical_coherent_pluggable_block_from_state({})


def test_optical_coherent_pluggable_block_from_state_rejects_unknown_subscription_instance_id(monkeypatch) -> None:
    """An unknown ``subscription_instance_id`` cannot be re-hydrated (no such instance)."""
    fake_session = Mock()
    fake_session.get.return_value = None
    monkeypatch.setattr(shared_parts, "db", SimpleNamespace(session=fake_session))

    with pytest.raises(ValueError, match="No subscription instance"):
        optical_coherent_pluggable_block_from_state({"subscription_instance_id": str(uuid.uuid4())})


def test_populate_block_step_fails_fast_when_state_has_no_block() -> None:
    """The populate step fails fast when the state holds no Optical Coherent Pluggable block."""
    with pytest.raises(ValueError, match="No Optical Coherent Pluggable block in the state"):
        cast(Any, populate_optical_coherent_pluggable_block_step).__wrapped__(
            optical_coherent_pluggable_block=None,
            optical_packet_node_id=str(uuid.uuid4()),
            optical_port_name="port-1",
            optical_port_description="desc",
            optical_coherent_pluggable_firmware_version="1.0",
        )


def test_update_block_step_fails_fast_when_state_has_no_block() -> None:
    """The update step fails fast when the state holds no Optical Coherent Pluggable block."""
    with pytest.raises(ValueError, match="No Optical Coherent Pluggable block in the state"):
        cast(Any, update_optical_coherent_pluggable_block).__wrapped__(
            optical_coherent_pluggable_block=None,
            optical_port_description="desc",
            optical_coherent_pluggable_firmware_version="1.0",
        )


@pytest.mark.parametrize(
    "subscription",
    [
        cast(Any, SimpleNamespace()),
        cast(Any, SimpleNamespace(optical_coherent_pluggable=None)),
    ],
)
def test_load_optical_coherent_pluggable_block_fails_fast_when_subscription_has_no_block(subscription) -> None:
    with pytest.raises(ValueError, match="under attribute 'optical_coherent_pluggable'") as exc_info:
        cast(Any, load_optical_coherent_pluggable_block).__wrapped__(subscription)

    assert "must have-a" in str(exc_info.value)


def test_load_optical_coherent_pluggable_block_returns_block_in_state() -> None:
    block = _make_pluggable_block()
    subscription = cast(Any, SimpleNamespace(optical_coherent_pluggable=block))

    state = cast(Any, load_optical_coherent_pluggable_block).__wrapped__(subscription)

    assert state == {OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY: block}


def test_validate_optical_coherent_pluggable_state_fails_fast_when_subscription_has_no_block() -> None:
    subscription = cast(Any, SimpleNamespace())

    with pytest.raises(ValueError, match="under attribute 'optical_coherent_pluggable'") as exc_info:
        cast(Any, validate_optical_coherent_pluggable_state).__wrapped__(
            subscription=subscription, optical_coherent_pluggable_block=None
        )

    assert "must have-a" in str(exc_info.value)
    assert "not fully provisioned" not in str(exc_info.value)


def test_validate_optical_coherent_pluggable_state_validates_the_block_from_the_state() -> None:
    block = _make_pluggable_block()
    block.optical_port_name = "port-1"
    subscription = cast(Any, SimpleNamespace())

    state = cast(Any, validate_optical_coherent_pluggable_state).__wrapped__(
        subscription=subscription, optical_coherent_pluggable_block=block
    )

    assert state == {}


def _round_tripped_block_state(
    block: OpticalCoherentPluggableBlockInactive, monkeypatch: pytest.MonkeyPatch
) -> dict[str, Any]:
    """Serialize a block the way the process engine does between steps.

    The block's computed part number resolves the owner subscription from the
    database, so ``model_dump`` needs a fake there (the tests are database-free).
    """
    monkeypatch.setattr(
        SubscriptionModel,
        "from_subscription",
        staticmethod(lambda _sid: SimpleNamespace(optical_coherent_pluggable_part_number="CISCO QDD-400G-ZRP-S")),
    )
    return cast(Any, json_loads(json_dumps({OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY: block})))


@pytest.mark.parametrize(
    "form_generator",
    [
        create_parts.create_optical_coherent_pluggable_form_generator,
        modify_parts.modify_optical_coherent_pluggable_form_generator,
        terminate_parts.terminate_initial_input_form_generator,
    ],
)
def test_form_generators_are_hook_free(form_generator) -> None:
    """The shipped form generators take no ``extra_form_pages``/``extra_summary_fields`` hooks."""
    parameters = inspect.signature(form_generator).parameters
    assert "extra_form_pages" not in parameters
    assert "extra_summary_fields" not in parameters


def _fake_customer_choice(include: str | None = None) -> type[Choice]:
    return cast(type[Choice], Choice.__call__("FakeCustomerChoice", {"cust-1": "cust-1", "cust-2": "cust-2"}))


def _fake_packet_node_choice(*args, **kwargs) -> type[Choice]:
    return cast(type[Choice], Choice.__call__("FakePacketNodeChoice", {"node-1": "node-1"}))


def _fake_packet_node_block_from_subscription(_subscription_id) -> OpticalModulePacketNodeInactive:
    return _make_packet_node_block()


def _finish_form(generator, page_instance: FormPage) -> dict[str, Any]:
    """Send the last user input and return the return value of the form generator."""
    with pytest.raises(StopIteration) as exc_info:
        generator.send(page_instance)
    return exc_info.value.value


def test_create_form_pages_yield_the_shipped_page(monkeypatch) -> None:
    monkeypatch.setattr(create_parts, "customer_choice_selector", _fake_customer_choice)
    monkeypatch.setattr(create_parts, "active_subscription_selector_by_block_type", _fake_packet_node_choice)
    monkeypatch.setattr(create_parts, "packet_node_block_from_subscription", _fake_packet_node_block_from_subscription)

    generator = create_parts.create_optical_coherent_pluggable_form_pages("Coherent Pluggable")

    page = next(generator)
    assert issubclass(page, FormPage)
    assert set(page.model_fields) == {
        "customer_id",
        "optical_packet_node_id",
        "optical_coherent_pluggable_part_number",
        "optical_port_name",
        "optical_port_description",
        "optical_coherent_pluggable_firmware_version",
    }

    user_input = _finish_form(
        generator,
        page(
            customer_id="cust-1",
            optical_packet_node_id="node-1",
            optical_coherent_pluggable_part_number=OpticalCoherentPluggablePartNumber.CISCO_QDD_400G_ZRP_S.value,
            optical_port_name="port-1",
            optical_port_description="desc",
            optical_coherent_pluggable_firmware_version="1.0",
        ),
    )
    assert user_input == {
        "customer_id": "cust-1",
        "optical_packet_node_id": "node-1",
        "optical_coherent_pluggable_part_number": OpticalCoherentPluggablePartNumber.CISCO_QDD_400G_ZRP_S.value,
        "optical_port_name": "port-1",
        "optical_port_description": "desc",
        "optical_coherent_pluggable_firmware_version": "1.0",
    }


def test_create_form_pages_compose_in_one_line_in_consumer_space(monkeypatch) -> None:
    monkeypatch.setattr(create_parts, "customer_choice_selector", _fake_customer_choice)
    monkeypatch.setattr(create_parts, "active_subscription_selector_by_block_type", _fake_packet_node_choice)
    monkeypatch.setattr(create_parts, "packet_node_block_from_subscription", _fake_packet_node_block_from_subscription)

    def my_create_form_generator(product_name):
        user_input_dict = yield from create_parts.create_optical_coherent_pluggable_form_pages(product_name)
        return user_input_dict

    generator = my_create_form_generator("Coherent Pluggable")
    page = next(generator)
    user_input = _finish_form(
        generator,
        page(
            customer_id="cust-1",
            optical_packet_node_id="node-1",
            optical_coherent_pluggable_part_number=OpticalCoherentPluggablePartNumber.CISCO_QDD_400G_ZRP_S.value,
            optical_port_name="port-1",
            optical_port_description="desc",
            optical_coherent_pluggable_firmware_version="1.0",
        ),
    )

    assert user_input["customer_id"] == "cust-1"
    assert user_input["optical_packet_node_id"] == "node-1"
    assert user_input["optical_port_name"] == "port-1"
    assert user_input["optical_coherent_pluggable_firmware_version"] == "1.0"


def test_modify_form_pages_yield_the_prefilled_page(monkeypatch) -> None:
    monkeypatch.setattr(modify_parts, "customer_choice_selector", _fake_customer_choice)

    block = _make_pluggable_block()
    block.optical_port_description = "desc"
    block.optical_coherent_pluggable_firmware_version = "1.0"
    subscription = cast(
        Any,
        SimpleNamespace(customer_id="cust-1", subscription_id=uuid.uuid4(), optical_coherent_pluggable=block),
    )

    generator = modify_parts.modify_optical_coherent_pluggable_form_pages(subscription)
    page = next(generator)
    assert issubclass(page, FormPage)
    assert page.model_fields["optical_port_description"].default == "desc"
    assert page.model_fields["optical_coherent_pluggable_firmware_version"].default == "1.0"

    user_input = _finish_form(
        generator,
        page(
            customer_id="cust-1",
            optical_port_description="desc2",
            optical_coherent_pluggable_firmware_version="2.0",
        ),
    )
    assert user_input["optical_port_description"] == "desc2"
    assert user_input["optical_coherent_pluggable_firmware_version"] == "2.0"


def test_terminate_form_pages_yield_the_confirmation_page() -> None:
    subscription_id = str(uuid.uuid4())

    generator = terminate_parts.terminate_optical_coherent_pluggable_form_pages(subscription_id)
    page = next(generator)
    assert issubclass(page, FormPage)
    assert set(page.model_fields) == {"subscription_id"}
    assert page.model_fields["subscription_id"].default == subscription_id
