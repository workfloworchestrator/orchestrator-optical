"""Composition contract tests for the Optical Spectrum Service workflow parts.

These tests are database-free: they verify the composition contract itself (the
state key contract of the shipped block steps, the hook-free form generators, the
page-sequence consumption model, the block population/update logic and the
shipped workflow composition), not the workflow execution. The DB-backed
selectors of the create/modify page sequences are replaced with fakes, so the
page sequences can be driven in-process.
"""

import inspect
import uuid
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pydantic_forms.validators import Choice, choice_list

from orchestrator.core.targets import Target
from orchestrator.core.workflow import Workflow
from orchestrator.optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrumBlockInactive,
    OpticalSpectrumBlockProvisioning,
)
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.optical_spectrum_service import create_optical_spectrum as spectrum_create
from orchestrator.optical.workflows.optical_spectrum_service import modify_optical_spectrum as spectrum_modify
from orchestrator.optical.workflows.optical_spectrum_service import (
    shared as spectrum_shared,
)
from orchestrator.optical.workflows.optical_spectrum_service import (
    terminate_optical_spectrum as spectrum_terminate,
)
from orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum import (
    CREATE_OPTICAL_SPECTRUM_BLOCK_STEPS,
    create_optical_spectrum,
    create_optical_spectrum_form_generator,
    create_optical_spectrum_form_pages,
    populate_optical_spectrum_block,
)
from orchestrator.optical.workflows.optical_spectrum_service.modify_optical_spectrum import (
    MODIFY_OPTICAL_SPECTRUM_BLOCK_STEPS,
    modify_optical_sections,
    modify_optical_spectrum,
    modify_optical_spectrum_form_generator,
    modify_optical_spectrum_form_pages,
    update_optical_spectrum_block,
)
from orchestrator.optical.workflows.optical_spectrum_service.reconcile_optical_spectrum import (
    RECONCILE_OPTICAL_SPECTRUM_BLOCK_STEPS,
    reconcile_optical_spectrum,
)
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    delete_optical_spectrum_sections,
    load_optical_spectrum_block,
)
from orchestrator.optical.workflows.optical_spectrum_service.terminate_optical_spectrum import (
    TERMINATE_OPTICAL_SPECTRUM_BLOCK_STEPS,
    terminate_initial_input_form_generator,
    terminate_optical_spectrum,
)
from orchestrator.optical.workflows.optical_spectrum_service.validate_optical_spectrum import (
    VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS,
    validate_optical_spectrum,
)
from test.support.core_api import step_functions, unwrap_step
from test.support.forms import finish_form

FREQUENCY_MIN = 196_000_000
FREQUENCY_MAX = 196_100_000
NEW_FREQUENCY_MIN = 196_025_000
NEW_FREQUENCY_MAX = 196_075_000

#: The only step in a ``*_BLOCK_STEPS`` list that is not block-level: it is the
#: wiring step that reads the block from the subscription into the state.
BLOCK_STEP_WIRING_ALLOWLIST = {unwrap_step(load_optical_spectrum_block)}

#: The page classes yielded by the shipped create page sequence, in order.
EXPECTED_CREATE_PAGE_NAMES = [
    "CreateOpticalSpectrumIdentityForm",
    "CreateOpticalSpectrumNodesForm",
    "CreateOpticalSpectrumAddDropForm",
    "CreateOpticalSpectrumWaypointsForm",
    "CreateOpticalSpectrumConstraintsForm",
    "CreateOpticalSpectrumPathForm",
]

#: The page classes yielded by the shipped modify page sequence, in order.
EXPECTED_MODIFY_PAGE_NAMES = [
    "ModifyOpticalSpectrumIdentityForm",
    "ModifyOpticalSpectrumWaypointsForm",
    "ModifyOpticalSpectrumConstraintsForm",
    "ModifyOpticalSpectrumPathForm",
]


def _fake_single_choice(*args: Any, **kwargs: Any) -> type[Choice]:
    return cast(type[Choice], Choice("FakeChoice", {"opt-a": "opt-a", "opt-b": "opt-b"}))


def _fake_multiple_choice(*args: Any, **kwargs: Any) -> type[list[Choice]]:
    base = Choice("FakeChoice", {"opt-a": "opt-a", "opt-b": "opt-b"})
    return cast(type[list[Choice]], choice_list(base))


def _fake_path_choice(*args: Any, **kwargs: Any) -> type[Choice]:
    return cast(type[Choice], Choice("FakePathChoice", {"p1;p2": ("p1;p2", "nodeA (p1) x nodeB (p2)")}))


class _FakeNode:
    """A minimal Optical Node block carrying the fields the page sequences read."""

    def __init__(self, subscription_instance_id: str) -> None:
        self.subscription_instance_id = subscription_instance_id
        self.management = SimpleNamespace(optical_module_node_fqdn=f"{subscription_instance_id}.example.com")


class _FakeAbstractOpticalNode:
    """Replaces ``AbstractOpticalNode.from_subscription`` in the create module namespace."""

    @staticmethod
    def from_subscription(subscription_id: str) -> SimpleNamespace:
        return SimpleNamespace(optical_node=_FakeNode(subscription_id))


def _make_spectrum_subscription(
    name: str = "spec-01",
    passband: tuple[int, int] = (FREQUENCY_MIN, FREQUENCY_MAX),
) -> SimpleNamespace:
    """Build a DB-free subscription whose block has two endpoint add/drop sections."""
    node_a = _FakeNode("node-a")
    node_b = _FakeNode("node-b")
    port_a = SimpleNamespace(optical_port_host_node=node_a)
    port_b = SimpleNamespace(optical_port_host_node=node_b)
    section_a = SimpleNamespace(optical_spectrum_section_add_drop_ports=[port_a])
    section_b = SimpleNamespace(optical_spectrum_section_add_drop_ports=[port_b])
    block = SimpleNamespace(
        optical_spectrum_name=name,
        optical_spectrum_passband=passband,
        optical_spectrum_sections=[section_a, section_b],
    )
    return SimpleNamespace(
        product=SimpleNamespace(name="Optical Spectrum"),
        subscription_id=uuid.uuid4(),
        customer_id="cust-1",
        optical_spectrum_service=block,
    )


def _monkeypatch_create_selectors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the DB/device-backed create page selectors with DB-free fakes.

    The selectors are looked up in the ``create_optical_spectrum`` module
    namespace, so every patch targets that namespace.
    """
    monkeypatch.setattr(spectrum_create, "optical_node_selector_of_roles", _fake_single_choice)
    monkeypatch.setattr(spectrum_create, "multiple_optical_node_selector", _fake_multiple_choice)
    monkeypatch.setattr(spectrum_create, "multiple_optical_pipe_selector_of_types", _fake_multiple_choice)
    monkeypatch.setattr(spectrum_create, "optical_port_selector", _fake_single_choice)
    monkeypatch.setattr(spectrum_create, "optical_spectrum_path_selector", _fake_path_choice)
    monkeypatch.setattr(spectrum_create, "validate_optical_spectrum_path", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(spectrum_create, "AbstractOpticalNode", _FakeAbstractOpticalNode)


def _monkeypatch_modify_selectors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the DB/device-backed modify page selectors with DB-free fakes."""
    monkeypatch.setattr(spectrum_modify, "multiple_optical_node_selector", _fake_multiple_choice)
    monkeypatch.setattr(spectrum_modify, "multiple_optical_pipe_selector_of_types", _fake_multiple_choice)
    monkeypatch.setattr(spectrum_modify, "optical_spectrum_path_selector", _fake_path_choice)
    monkeypatch.setattr(spectrum_modify, "validate_optical_spectrum_path", lambda *_args, **_kwargs: None)


def test_block_state_key_matches_the_documented_contract() -> None:
    """The state key literal matches the value documented in the README state-contract table."""
    assert OPTICAL_MODULE_BLOCK_STATE_KEY == "optical_module_block"


@pytest.mark.parametrize(
    "form_generator",
    [
        create_optical_spectrum_form_generator,
        modify_optical_spectrum_form_generator,
        terminate_initial_input_form_generator,
    ],
)
def test_form_generators_are_hook_free(form_generator) -> None:
    """The shipped form generators take no ``extra_form_pages``/``extra_summary_fields`` hooks."""
    parameters = inspect.signature(form_generator).parameters
    assert "extra_form_pages" not in parameters
    assert "extra_summary_fields" not in parameters


def test_block_steps_consume_the_block_state_key() -> None:
    """Every block step but the wiring step takes the block under ``optical_module_block``."""
    all_steps = (
        CREATE_OPTICAL_SPECTRUM_BLOCK_STEPS
        + MODIFY_OPTICAL_SPECTRUM_BLOCK_STEPS
        + TERMINATE_OPTICAL_SPECTRUM_BLOCK_STEPS
        + VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS
        + RECONCILE_OPTICAL_SPECTRUM_BLOCK_STEPS
    )
    unexpected_exceptions = []
    for step_func in step_functions(all_steps):
        signature = inspect.signature(step_func)
        if step_func in BLOCK_STEP_WIRING_ALLOWLIST:
            assert "subscription" in signature.parameters
            continue
        if OPTICAL_MODULE_BLOCK_STATE_KEY not in signature.parameters:
            unexpected_exceptions.append(step_func.__name__)
    assert not unexpected_exceptions, (
        "steps without the optical_module_block state-key parameter (add to the allowlist only if wiring): "
        f"{unexpected_exceptions}"
    )


def test_create_block_steps_have_the_expected_order() -> None:
    """The shipped create block steps run in the documented order."""
    names = [step.name for step in CREATE_OPTICAL_SPECTRUM_BLOCK_STEPS]
    assert names == [
        "Adding a description to the add/drop ports",
        "Provisioning optical spectrum sections",
        "Updating the available passbands of any Open Line System port in the path",
        "Persist optical module block",
    ]


def test_modify_block_steps_have_the_expected_order() -> None:
    """The shipped modify block steps run in the documented order."""
    names = [step.name for step in MODIFY_OPTICAL_SPECTRUM_BLOCK_STEPS]
    assert names == [
        "Updating Optical Spectrum block",
        "Dividing the optical path into single-platform sections",
        "Modifying optical spectrum sections",
        "Updating the available passbands of any Open Line System port in the path",
        "Persist optical module block",
    ]


def test_terminate_block_steps_have_the_expected_order() -> None:
    """The shipped terminate block steps run in the documented order."""
    names = [step.name for step in TERMINATE_OPTICAL_SPECTRUM_BLOCK_STEPS]
    assert names == [
        "Deleting optical sections",
        "Updating the available passbands of any Open Line System port in the path",
        "Persist optical module block",
    ]


def test_validate_block_steps_have_the_expected_order() -> None:
    """The shipped validate block steps run in the documented order."""
    names = [step.name for step in VALIDATE_OPTICAL_SPECTRUM_BLOCK_STEPS]
    assert names == ["Load optical spectrum block", "Verifying optical spectrum sections"]


def test_reconcile_block_steps_have_the_expected_order() -> None:
    """The shipped reconcile block steps run in the documented order."""
    names = [step.name for step in RECONCILE_OPTICAL_SPECTRUM_BLOCK_STEPS]
    assert names == [
        "Provisioning optical spectrum sections",
        "Updating the available passbands of any Open Line System port in the path",
        "Persist optical module block",
        "Verifying optical spectrum sections",
    ]


def test_create_form_pages_yield_the_shipped_pages_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """The create page sequence resolves the choices between yields and returns a flat dict."""
    _monkeypatch_create_selectors(monkeypatch)
    generator = create_optical_spectrum_form_pages("Optical Spectrum")
    page_names: list[str] = []

    page_1 = next(generator)
    page_names.append(page_1.__name__)
    assert set(page_1.model_fields) == {"optical_spectrum_name", "frequency_min", "frequency_max"}

    page_2 = generator.send(
        page_1(
            optical_spectrum_name="spec-01",
            frequency_min=FREQUENCY_MIN,
            frequency_max=FREQUENCY_MAX,
        )
    )
    page_names.append(page_2.__name__)
    assert set(page_2.model_fields) == {"src_optical_device_id", "dst_optical_device_id"}

    page_3 = generator.send(page_2(src_optical_device_id="opt-a", dst_optical_device_id="opt-b"))
    page_names.append(page_3.__name__)
    assert set(page_3.model_fields) == {"src_optical_port_name", "dst_optical_port_name"}

    page_4 = generator.send(page_3(src_optical_port_name="opt-a", dst_optical_port_name="opt-b"))
    page_names.append(page_4.__name__)
    assert set(page_4.model_fields) == {"intermediate_node_ids"}

    page_5 = generator.send(page_4(intermediate_node_ids=["opt-a"]))
    page_names.append(page_5.__name__)
    assert set(page_5.model_fields) == {"exclude_devices_list", "divider1", "exclude_fibers_list"}

    page_6 = generator.send(page_5(exclude_devices_list=["opt-a"], exclude_fibers_list=["opt-b"], divider1=None))
    page_names.append(page_6.__name__)
    assert set(page_6.model_fields) == {"optical_path"}

    user_input = finish_form(generator, page_6(optical_path="p1;p2"))

    assert page_names == EXPECTED_CREATE_PAGE_NAMES
    assert "customer_id" not in user_input
    assert set(user_input) == {
        "optical_spectrum_name",
        "frequency_min",
        "frequency_max",
        "src_optical_device_id",
        "dst_optical_device_id",
        "src_optical_port_name",
        "dst_optical_port_name",
        "intermediate_node_ids",
        "exclude_devices_list",
        "divider1",
        "exclude_fibers_list",
        "optical_path",
    }
    assert user_input["optical_path"] == ["p1", "p2"]


def test_modify_form_pages_yield_the_prefilled_pages_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """The modify page sequence yields the prefilled pages and returns a flat dict."""
    _monkeypatch_modify_selectors(monkeypatch)
    subscription = _make_spectrum_subscription()
    generator = modify_optical_spectrum_form_pages(subscription)
    page_names: list[str] = []

    page_1 = next(generator)
    page_names.append(page_1.__name__)
    assert set(page_1.model_fields) == {"optical_spectrum_name", "frequency_min", "frequency_max"}
    assert page_1.model_fields["optical_spectrum_name"].default == "spec-01"
    assert page_1.model_fields["frequency_min"].default == FREQUENCY_MIN
    assert page_1.model_fields["frequency_max"].default == FREQUENCY_MAX

    page_2 = generator.send(
        page_1(
            optical_spectrum_name="spec-02",
            frequency_min=FREQUENCY_MIN,
            frequency_max=FREQUENCY_MAX,
        )
    )
    page_names.append(page_2.__name__)
    assert set(page_2.model_fields) == {"intermediate_node_ids"}

    page_3 = generator.send(page_2(intermediate_node_ids=["opt-a"]))
    page_names.append(page_3.__name__)
    assert set(page_3.model_fields) == {"exclude_devices_list", "divider1", "exclude_fibers_list"}

    page_4 = generator.send(page_3(exclude_devices_list=["opt-a"], exclude_fibers_list=["opt-b"], divider1=None))
    page_names.append(page_4.__name__)
    assert set(page_4.model_fields) == {"optical_path"}

    user_input = finish_form(generator, page_4(optical_path="p1;p2"))

    assert page_names == EXPECTED_MODIFY_PAGE_NAMES
    assert "customer_id" not in user_input
    assert set(user_input) == {
        "optical_spectrum_name",
        "frequency_min",
        "frequency_max",
        "intermediate_node_ids",
        "exclude_devices_list",
        "divider1",
        "exclude_fibers_list",
        "optical_path",
    }
    assert user_input["optical_path"] == ["p1", "p2"]


def test_populate_optical_spectrum_block_writes_only_name_and_passband() -> None:
    """The create anti-corruption function sets only the name and the passband."""
    sections = [object()]
    block = OpticalSpectrumBlockInactive.model_construct(
        name="OpticalSpectrumBlock",
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=uuid.uuid4(),
        optical_spectrum_sections=sections,
    )

    populate_optical_spectrum_block(block, "spec-01", FREQUENCY_MIN, FREQUENCY_MAX)

    assert block.optical_spectrum_name == "spec-01"
    assert block.optical_spectrum_passband == (FREQUENCY_MIN, FREQUENCY_MAX)
    assert block.optical_spectrum_sections is sections


def _make_section(add_drop_ids: list[str], express_ids: list[str]) -> SimpleNamespace:
    """Build a DB-free spectrum section carrying only the fields the steps read."""

    def port(port_id: str) -> SimpleNamespace:
        node = SimpleNamespace(
            subscription_instance_id=f"node-{port_id}",
            management=SimpleNamespace(optical_module_node_fqdn=f"{port_id}.example.com"),
        )
        return SimpleNamespace(subscription_instance_id=port_id, optical_port_host_node=node)

    return SimpleNamespace(
        optical_spectrum_section_add_drop_ports=[port(port_id) for port_id in add_drop_ids],
        optical_spectrum_section_express_ports=[port(port_id) for port_id in express_ids],
    )


def _make_modify_block(section: SimpleNamespace) -> OpticalSpectrumBlockProvisioning:
    return OpticalSpectrumBlockProvisioning.model_construct(
        name="OpticalSpectrumBlock",
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=uuid.uuid4(),
        optical_spectrum_name="spec-01",
        optical_spectrum_passband=(FREQUENCY_MIN, FREQUENCY_MAX),
        optical_spectrum_sections=[section],
    )


def _install_recording_hal(
    monkeypatch: pytest.MonkeyPatch,
    calls: dict[str, list],
    old_section: SimpleNamespace,
) -> None:
    """Patch the HAL calls of ``modify_optical_sections`` with recording fakes."""
    monkeypatch.setattr(spectrum_modify, "load_spectrum_section", lambda _sid: old_section)

    def record(name: str):
        def _recorder(*args: Any, **kwargs: Any) -> dict[str, Any]:
            calls[name].append(args)
            return {}

        return _recorder

    monkeypatch.setattr(spectrum_shared, "delete_optical_circuit", record("delete"))
    monkeypatch.setattr(spectrum_shared, "delete_optical_circuit_oel", record("delete_oel"))
    monkeypatch.setattr(spectrum_modify, "deploy_optical_circuit", record("deploy"))
    monkeypatch.setattr(spectrum_modify, "modify_optical_circuit", record("modify"))


def test_modify_optical_sections_modifies_in_place_when_path_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unchanged path keeps the in-place circuit modification."""
    section = _make_section(["ad-1", "ad-2"], ["exp-1"])
    calls: dict[str, list] = {"delete": [], "delete_oel": [], "deploy": [], "modify": []}
    _install_recording_hal(monkeypatch, calls, section)

    state = unwrap_step(modify_optical_sections)(
        optical_module_block=_make_modify_block(section),
        old_passband=(FREQUENCY_MIN, FREQUENCY_MAX),
        old_section_ids=["old-section-id"],
    )

    assert calls["modify"]
    assert not calls["delete"]
    assert not calls["delete_oel"]
    assert not calls["deploy"]
    assert "configuration_results" in state


def test_modify_optical_sections_redeploys_when_path_changed(monkeypatch: pytest.MonkeyPatch) -> None:
    """A changed path tears down the old circuits (and OEL) and deploys the new ones."""
    old_section = _make_section(["old-ad-1", "old-ad-2"], ["old-exp"])
    new_section = _make_section(["new-ad-1", "new-ad-2"], ["new-exp"])
    calls: dict[str, list] = {"delete": [], "delete_oel": [], "deploy": [], "modify": []}
    _install_recording_hal(monkeypatch, calls, old_section)

    state = unwrap_step(modify_optical_sections)(
        optical_module_block=_make_modify_block(new_section),
        old_passband=(FREQUENCY_MIN, FREQUENCY_MAX),
        old_section_ids=["old-section-id"],
    )

    assert calls["delete"]
    assert calls["delete_oel"]
    assert calls["deploy"]
    assert not calls["modify"]
    assert "configuration_results" in state


def test_delete_optical_spectrum_sections_deletes_each_node_oel_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every section is deleted, but a shared source node's OEL is deleted only once."""
    section_a = _make_section(["shared-ad", "ad-2"], ["exp-1"])
    section_b = _make_section(["shared-ad", "ad-3"], ["exp-2"])
    calls: dict[str, list] = {"delete": [], "delete_oel": []}

    def record(name: str):
        def _recorder(*args: Any, **kwargs: Any) -> dict[str, Any]:
            calls[name].append(args)
            return {}

        return _recorder

    monkeypatch.setattr(spectrum_shared, "delete_optical_circuit", record("delete"))
    monkeypatch.setattr(spectrum_shared, "delete_optical_circuit_oel", record("delete_oel"))

    results = delete_optical_spectrum_sections(
        [section_a, section_b],
        (FREQUENCY_MIN, FREQUENCY_MAX),
        "spec-01",
        "cid",
    )

    assert len(calls["delete"]) == 2
    assert len(calls["delete_oel"]) == 1
    assert set(results) == {"shared-ad.example.com", "shared-ad.example.com:OEL"}


def test_terminate_delete_optical_sections_uses_the_shared_teardown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The terminate step delegates to the shared teardown with the block's own identity."""
    section = _make_section(["ad-1", "ad-2"], ["exp-1"])
    block = _make_modify_block(section)
    recorded: dict[str, Any] = {}

    def _fake_teardown(sections: Any, passband: Any, spectrum_name: Any, circuit_identifier: Any) -> dict[str, Any]:
        recorded.update(
            sections=sections,
            passband=passband,
            spectrum_name=spectrum_name,
            circuit_identifier=circuit_identifier,
        )
        return {"node": {}}

    monkeypatch.setattr(spectrum_terminate, "delete_optical_spectrum_sections", _fake_teardown)

    state = unwrap_step(spectrum_terminate.delete_optical_sections)(optical_module_block=block)

    assert recorded["sections"] == [section]
    assert recorded["passband"] == (FREQUENCY_MIN, FREQUENCY_MAX)
    assert recorded["spectrum_name"] == "spec-01"
    assert recorded["circuit_identifier"] == str(block.subscription_instance_id)
    assert state == {"configuration_results": {"node": {}}}


def test_update_optical_spectrum_block_writes_only_name_and_passband() -> None:
    """The modify step overwrites only the name and the passband and returns the old passband."""
    section = SimpleNamespace(subscription_instance_id=uuid.uuid4())
    block = OpticalSpectrumBlockProvisioning.model_construct(
        name="OpticalSpectrumBlock",
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=uuid.uuid4(),
        optical_spectrum_name="old-name",
        optical_spectrum_passband=(FREQUENCY_MIN, FREQUENCY_MAX),
        optical_spectrum_sections=[section],
    )

    state = unwrap_step(update_optical_spectrum_block)(
        optical_module_block=block,
        optical_spectrum_name="spec-02",
        frequency_min=NEW_FREQUENCY_MIN,
        frequency_max=NEW_FREQUENCY_MAX,
    )

    assert block.optical_spectrum_name == "spec-02"
    assert block.optical_spectrum_passband == (NEW_FREQUENCY_MIN, NEW_FREQUENCY_MAX)
    assert block.optical_spectrum_sections == [section]
    assert state == {
        OPTICAL_MODULE_BLOCK_STATE_KEY: block,
        "old_passband": (FREQUENCY_MIN, FREQUENCY_MAX),
        "old_section_ids": [str(section.subscription_instance_id)],
    }


@pytest.mark.parametrize(
    ("workflow_func", "expected_name", "expected_target"),
    [
        (create_optical_spectrum, "create_optical_spectrum", Target.CREATE),
        (modify_optical_spectrum, "modify_optical_spectrum", Target.MODIFY),
        (terminate_optical_spectrum, "terminate_optical_spectrum", Target.TERMINATE),
        (validate_optical_spectrum, "validate_optical_spectrum", Target.VALIDATE),
        (reconcile_optical_spectrum, "reconcile_optical_spectrum", Target.RECONCILE),
    ],
)
def test_shipped_workflows_are_workflow_instances_with_the_right_target(
    workflow_func, expected_name: str, expected_target: Target
) -> None:
    """Every shipped workflow is a ``Workflow`` with the expected name and target."""
    workflow: Workflow = workflow_func
    assert isinstance(workflow, Workflow)
    assert workflow.name == expected_name
    assert workflow.target == expected_target


def test_shipped_create_workflow_composes_the_block_steps_in_order() -> None:
    """The shipped create workflow runs the block steps after the construct and provisioning status."""
    names = [step.name for step in create_optical_spectrum.steps]
    construct = names.index("Construct Optical Spectrum Subscription")
    set_provisioning = names.index("Set subscription to 'provisioning'")
    configure = names.index("Adding a description to the add/drop ports")
    provision = names.index("Provisioning optical spectrum sections")
    retrieve = names.index("Updating the available passbands of any Open Line System port in the path")
    persist = names.index("Persist optical module block")
    set_description = names.index("Set Optical Spectrum subscription description")
    create_relation = names.index("Create Process Subscription relation")
    assert construct < set_provisioning < configure < provision < retrieve < persist < set_description
    assert persist < create_relation


def test_shipped_modify_workflow_loads_updates_and_persists_the_block() -> None:
    """The shipped modify workflow loads the block, updates it, persists it and sets the description."""
    names = [step.name for step in modify_optical_spectrum.steps]
    load = names.index("Load optical spectrum block")
    update = names.index("Updating Optical Spectrum block")
    persist = names.index("Persist optical module block")
    set_description = names.index("Set Optical Spectrum subscription description")
    assert load < update < persist < set_description


def test_shipped_terminate_and_validate_workflows_compose_the_shared_steps() -> None:
    """The shipped terminate/validate workflows load the block before the block steps run."""
    terminate_names = [step.name for step in terminate_optical_spectrum.steps]
    validate_names = [step.name for step in validate_optical_spectrum.steps]
    assert terminate_names.index("Load optical spectrum block") < terminate_names.index("Deleting optical sections")
    assert validate_names.index("Load optical spectrum block") < validate_names.index(
        "Verifying optical spectrum sections"
    )
    assert "Set Optical Spectrum subscription description" in validate_names


def test_shipped_reconcile_workflow_loads_pushes_and_verifies_the_block() -> None:
    """The shipped reconcile workflow loads, re-pushes, persists and re-verifies the block."""
    names = [step.name for step in reconcile_optical_spectrum.steps]
    load = names.index("Load optical spectrum block")
    provision = names.index("Provisioning optical spectrum sections")
    refresh = names.index("Updating the available passbands of any Open Line System port in the path")
    persist = names.index("Persist optical module block")
    verify = names.index("Verifying optical spectrum sections")
    set_description = names.index("Set Optical Spectrum subscription description")
    assert load < provision < refresh < persist < verify < set_description


def test_load_optical_spectrum_block_puts_the_block_in_the_state() -> None:
    """The wiring step reads the block from the ``optical_spectrum_service`` attribute."""
    block = OpticalSpectrumBlockInactive.model_construct(
        name="OpticalSpectrumBlock",
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=uuid.uuid4(),
    )
    subscription = SimpleNamespace(optical_spectrum_service=block)

    state = unwrap_step(load_optical_spectrum_block)(subscription=subscription)

    assert state == {OPTICAL_MODULE_BLOCK_STATE_KEY: block}
