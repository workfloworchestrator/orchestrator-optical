"""Composition contract tests for the Optical Pipe workflow parts.

These tests are database-free: they verify the composition contract itself
(the state key contract of the shipped block steps, the hook-free form
generators, the page-sequence consumption model, the block population logic
and the composition of the shipped step lists into consumer workflows), not
the workflow execution.
"""

import inspect
import uuid
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import pytest
from pydantic_forms.validators import Choice

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import Workflow, begin
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow, modify_workflow, terminate_workflow, validate_workflow
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_span import OpticalFiberSpanBlockInactive
from orchestrator.optical.workflows import customer as customer_parts
from orchestrator.optical.workflows.optical_pipe import shared as pipe_shared
from orchestrator.optical.workflows.optical_pipe.fiber_patch.create import (
    CREATE_FIBER_PATCH_BLOCK_STEPS,
    construct_fiber_patch_subscription,
    create_fiber_patch_form_generator,
)
from orchestrator.optical.workflows.optical_pipe.fiber_patch.modify import modify_fiber_patch_form_generator
from orchestrator.optical.workflows.optical_pipe.fiber_patch.terminate import (
    terminate_initial_input_form_generator as fiber_patch_terminate_initial_input_form_generator,
)
from orchestrator.optical.workflows.optical_pipe.fiber_span import create as fiber_span_create
from orchestrator.optical.workflows.optical_pipe.fiber_span import modify as fiber_span_modify
from orchestrator.optical.workflows.optical_pipe.fiber_span import terminate as fiber_span_terminate
from orchestrator.optical.workflows.optical_pipe.fiber_span.create import (
    CREATE_FIBER_SPAN_BLOCK_STEPS,
    configure_span_terminations,
    construct_fiber_span_subscription,
    create_fiber_span_form_generator,
    retrieve_span_used_passbands,
)
from orchestrator.optical.workflows.optical_pipe.fiber_span.modify import (
    MODIFY_FIBER_SPAN_BLOCK_STEPS,
    modify_fiber_span_form_generator,
)
from orchestrator.optical.workflows.optical_pipe.fiber_span.terminate import FIBER_SPAN_TERMINATE_STEPS
from orchestrator.optical.workflows.optical_pipe.fiber_span.terminate import (
    terminate_initial_input_form_generator as fiber_span_terminate_initial_input_form_generator,
)
from orchestrator.optical.workflows.optical_pipe.fiber_span.validate import FIBER_SPAN_VALIDATE_STEPS
from orchestrator.optical.workflows.optical_pipe.leased_spectrum.create import create_leased_spectrum_form_generator
from orchestrator.optical.workflows.optical_pipe.leased_spectrum.modify import (
    MODIFY_LEASED_SPECTRUM_BLOCK_STEPS,
    modify_leased_spectrum_form_generator,
)
from orchestrator.optical.workflows.optical_pipe.leased_spectrum.terminate import (
    terminate_initial_input_form_generator as leased_spectrum_terminate_initial_input_form_generator,
)
from orchestrator.optical.workflows.optical_pipe.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    load_optical_pipe_block,
    set_optical_pipe_subscription_description,
)


def _step_functions(steps):
    return [cast(Any, step).__wrapped__ for step in steps]


def _fake_customer_choice(include: str | None = None) -> type[Choice]:
    return cast(type[Choice], Choice.__call__("FakeCustomerChoice", {"cust-1": "cust-1", "cust-2": "cust-2"}))


def _fake_node_choice(prompt: str | None = None) -> type[Choice]:
    return cast(type[Choice], Choice.__call__("FakeNodeChoice", {"node-a": "node-a", "node-b": "node-b"}))


def _fake_port_choice(node_subscription_id: str, ports: list[str], prompt: str | None = None) -> type[Choice]:
    options = {port: f"{node_subscription_id} {port}" for port in ports}
    return cast(type[Choice], Choice(prompt, zip(options.keys(), options.items(), strict=False)))


def _fake_node_block_from_subscription(node_subscription_id: str) -> SimpleNamespace:
    return SimpleNamespace(management=SimpleNamespace(optical_module_node_fqdn=f"{node_subscription_id}.example.com"))


def _monkeypatch_create_selectors(monkeypatch: pytest.MonkeyPatch, module: Any) -> None:
    """Patch the DB/device-backed form selectors of a pipe create module with DB-free fakes."""
    monkeypatch.setattr(module, "optical_node_selector", _fake_node_choice)
    monkeypatch.setattr(module, "node_block_from_subscription", _fake_node_block_from_subscription)
    monkeypatch.setattr(module, "get_device_line_ports_names", Mock(return_value=["port-a-1", "port-b-1"]))
    monkeypatch.setattr(module, "unused_node_port_selector", _fake_port_choice)


def _make_span_block(optical_pipe_name: str | None = None) -> OpticalFiberSpanBlockInactive:
    return OpticalFiberSpanBlockInactive.model_construct(
        optical_pipe_name=optical_pipe_name,
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=uuid.uuid4(),
    )


def _finish_form(generator, page_instance: FormPage) -> dict[str, Any]:
    """Send the last user input and return the return value of the form generator."""
    with pytest.raises(StopIteration) as exc_info:
        generator.send(page_instance)
    return exc_info.value.value


def test_pipe_block_state_key_matches_the_documented_contract() -> None:
    """The state key literal matches the value documented in the README state-contract table."""
    assert OPTICAL_MODULE_BLOCK_STATE_KEY == "optical_module_block"


@pytest.mark.parametrize(
    "form_generator",
    [
        create_fiber_span_form_generator,
        modify_fiber_span_form_generator,
        fiber_span_terminate_initial_input_form_generator,
        create_fiber_patch_form_generator,
        modify_fiber_patch_form_generator,
        fiber_patch_terminate_initial_input_form_generator,
        create_leased_spectrum_form_generator,
        modify_leased_spectrum_form_generator,
        leased_spectrum_terminate_initial_input_form_generator,
    ],
)
def test_form_generators_are_hook_free(form_generator) -> None:
    """The shipped form generators take no ``extra_form_pages``/``extra_summary_fields`` hooks."""
    parameters = inspect.signature(form_generator).parameters
    assert "extra_form_pages" not in parameters
    assert "extra_summary_fields" not in parameters


def test_block_steps_consume_the_block_state_key() -> None:
    """The shared save/update block steps take the pipe block under the state key."""
    for step_func in _step_functions(CREATE_FIBER_SPAN_BLOCK_STEPS + MODIFY_FIBER_SPAN_BLOCK_STEPS):
        signature = inspect.signature(step_func)
        assert OPTICAL_MODULE_BLOCK_STATE_KEY in signature.parameters


def test_create_form_pages_yield_the_shipped_pages_in_order(monkeypatch) -> None:
    """The create page sequence resolves the node/port choices between yields and returns a flat dict."""
    _monkeypatch_create_selectors(monkeypatch, fiber_span_create)

    generator = fiber_span_create.create_fiber_span_form_pages("Optical Fiber Span")

    page_1 = next(generator)
    assert issubclass(page_1, FormPage)
    assert set(page_1.model_fields) == {"node_a_id", "node_b_id"}

    page_2 = generator.send(page_1(node_a_id="node-a", node_b_id="node-b"))
    assert issubclass(page_2, FormPage)
    assert set(page_2.model_fields) == {"optical_pipe_name", "port_a_name", "port_b_name"}

    user_input = _finish_form(
        generator,
        page_2(optical_pipe_name="span-01", port_a_name="port-a-1", port_b_name="port-b-1"),
    )
    assert user_input == {
        "node_a_id": "node-a",
        "node_b_id": "node-b",
        "optical_pipe_name": "span-01",
        "port_a_name": "port-a-1",
        "port_b_name": "port-b-1",
    }


def test_create_form_pages_compose_in_one_line_in_consumer_space(monkeypatch) -> None:
    """Consumers yield from the shipped page sequence in one line and get the flat keys back."""
    monkeypatch.setattr(customer_parts, "customer_choice_selector", _fake_customer_choice)
    _monkeypatch_create_selectors(monkeypatch, fiber_span_create)

    def my_create_form_generator(product_name):
        user_input_dict = yield from customer_parts.customer_choice_form_page()
        user_input_dict.update((yield from fiber_span_create.create_fiber_span_form_pages(product_name)))
        return user_input_dict

    generator = my_create_form_generator("Optical Fiber Span")
    customer_page = next(generator)
    page_1 = generator.send(customer_page(customer_id="cust-1"))
    page_2 = generator.send(page_1(node_a_id="node-a", node_b_id="node-b"))
    user_input = _finish_form(
        generator,
        page_2(optical_pipe_name="span-01", port_a_name="port-a-1", port_b_name="port-b-1"),
    )

    assert user_input["customer_id"] == "cust-1"
    assert user_input["node_a_id"] == "node-a"
    assert user_input["node_b_id"] == "node-b"
    assert user_input["optical_pipe_name"] == "span-01"
    assert user_input["port_a_name"] == "port-a-1"
    assert user_input["port_b_name"] == "port-b-1"


def test_modify_form_pages_yield_the_prefilled_page() -> None:
    """The modify page sequence yields a page prefilled with the current pipe name."""
    block = _make_span_block("span-01")
    subscription = cast(
        Any,
        SimpleNamespace(customer_id="cust-1", subscription_id=uuid.uuid4(), optical_pipe=block),
    )

    generator = fiber_span_modify.modify_fiber_span_form_pages(subscription)
    page = next(generator)
    assert issubclass(page, FormPage)
    assert set(page.model_fields) == {"optical_pipe_name"}
    assert page.model_fields["optical_pipe_name"].default == "span-01"

    user_input = _finish_form(generator, page(optical_pipe_name="span-02"))
    assert user_input["optical_pipe_name"] == "span-02"


def test_terminate_form_pages_yield_the_confirmation_page() -> None:
    """The terminate page sequence yields the confirmation page with the subscription id default."""
    subscription_id = str(uuid.uuid4())

    generator = fiber_span_terminate.terminate_fiber_span_form_pages(subscription_id)
    page = next(generator)
    assert issubclass(page, FormPage)
    assert set(page.model_fields) == {"warning", "subscription_id"}
    assert page.model_fields["subscription_id"].default == subscription_id


def test_shipped_type_create_workflow_composition() -> None:
    """The shipped create workflow composes from the parts with the documented step ordering."""

    @create_workflow(initial_input_form=create_fiber_span_form_generator)
    def create_fiber_span():
        return (
            begin
            >> construct_fiber_span_subscription
            >> CREATE_FIBER_SPAN_BLOCK_STEPS
            >> set_optical_pipe_subscription_description
            >> store_process_subscription()
            >> configure_span_terminations
            >> retrieve_span_used_passbands
        )

    workflow: Workflow = create_fiber_span
    assert workflow.name == "create_fiber_span"
    names = [step.name for step in workflow.steps]
    assert names.index("Construct Fiber Span Subscription") < names.index("Persist optical pipe block")
    assert names.index("Persist optical pipe block") < names.index("Set Optical Pipe subscription description")
    assert names.index("Set Optical Pipe subscription description") < names.index(
        "Create Process Subscription relation"
    )


def test_shipped_type_modify_workflow_composition() -> None:
    """The shipped modify workflow loads the block, updates it, persists it and sets the description."""

    @modify_workflow(initial_input_form=modify_fiber_span_form_generator)
    def modify_fiber_span():
        return (
            begin
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> load_optical_pipe_block
            >> MODIFY_FIBER_SPAN_BLOCK_STEPS
            >> set_optical_pipe_subscription_description
            >> set_status(SubscriptionLifecycle.ACTIVE)
        )

    workflow: Workflow = modify_fiber_span
    assert workflow.name == "modify_fiber_span"
    names = [step.name for step in workflow.steps]
    assert names.index("Load optical pipe block") < names.index("Updating Optical Pipe block")
    assert names.index("Updating Optical Pipe block") < names.index("Persist optical pipe block")


def test_terminate_and_validate_shared_step_lists_compose() -> None:
    """The shipped terminate/validate step lists compose into consumer workflows."""

    @terminate_workflow(initial_input_form=fiber_span_terminate_initial_input_form_generator)
    def terminate_fiber_span():
        return begin >> FIBER_SPAN_TERMINATE_STEPS

    @validate_workflow()
    def validate_fiber_span():
        return begin >> FIBER_SPAN_VALIDATE_STEPS

    assert terminate_fiber_span.name == "terminate_fiber_span"
    assert validate_fiber_span.name == "validate_fiber_span"
    assert "Factory Reset Fiber Span Ports" in [step.name for step in terminate_fiber_span.steps]
    assert "Load Initial State" in [step.name for step in validate_fiber_span.steps]


def test_fiber_patch_and_leased_spectrum_step_lists_compose() -> None:
    """The other pipe families share the same block steps and compose from the same parts."""

    @create_workflow(initial_input_form=create_fiber_patch_form_generator)
    def create_fiber_patch():
        return begin >> construct_fiber_patch_subscription >> CREATE_FIBER_PATCH_BLOCK_STEPS

    @modify_workflow(initial_input_form=modify_leased_spectrum_form_generator)
    def modify_leased_spectrum():
        return begin >> MODIFY_LEASED_SPECTRUM_BLOCK_STEPS

    patch_workflow: Workflow = create_fiber_patch
    names = [step.name for step in patch_workflow.steps]
    assert names.index("Construct Fiber Patch Subscription") < names.index("Persist optical pipe block")

    leased_workflow: Workflow = modify_leased_spectrum
    names = [step.name for step in leased_workflow.steps]
    assert names.index("Updating Optical Pipe block") < names.index("Persist optical pipe block")


def test_update_optical_pipe_block_writes_only_optical_pipe_name(monkeypatch) -> None:
    """The shared update step writes only ``optical_pipe_name`` and returns the block in the state."""
    block = SimpleNamespace(optical_pipe_name="old-name")
    monkeypatch.setattr(pipe_shared, "optical_pipe_block_from_state", Mock(return_value=block))

    state = cast(Any, pipe_shared.update_optical_pipe_block).__wrapped__(
        optical_module_block=block, optical_pipe_name="new-name"
    )

    assert block.optical_pipe_name == "new-name"
    assert state == {OPTICAL_MODULE_BLOCK_STATE_KEY: block}


def test_build_fiber_span_block(monkeypatch) -> None:
    """The anti-corruption block builder wires the two terminations without a database."""
    node_a = SimpleNamespace(management=SimpleNamespace(optical_module_node_fqdn="node-a.example.com"))
    node_b = SimpleNamespace(management=SimpleNamespace(optical_module_node_fqdn="node-b.example.com"))
    monkeypatch.setattr(fiber_span_create, "node_block_from_subscription", Mock(side_effect=[node_a, node_b]))

    def fake_new_pipe_port_block(subscription_id, host_node_block, port_name, port_description, port_block_class):
        return port_block_class.model_construct(
            optical_port_name=port_name,
            optical_port_host_node=host_node_block,
            optical_port_description=port_description,
            subscription_instance_id=uuid.uuid4(),
            owner_subscription_id=subscription_id,
        )

    monkeypatch.setattr(fiber_span_create, "new_pipe_port_block", fake_new_pipe_port_block)

    def fake_new(cls, subscription_id, optical_pipe_terminations):
        return cls.model_construct(
            optical_pipe_terminations=optical_pipe_terminations,
            subscription_instance_id=uuid.uuid4(),
            owner_subscription_id=subscription_id,
        )

    monkeypatch.setattr(fiber_span_create.OpticalFiberSpanBlockInactive, "new", classmethod(fake_new))

    subscription_id = uuid.uuid4()
    block = fiber_span_create.build_fiber_span_block(subscription_id, "node-a", "node-b", "p1", "p2", "span-01")

    assert block.optical_pipe_name == "span-01"
    assert len(block.optical_pipe_terminations) == 2
    assert {t.optical_port_name for t in block.optical_pipe_terminations} == {"p1", "p2"}
