"""Tests for the composition-based consumption model of the Optical module workflows.

The module ships workflow parts (form generators and step lists); consumers
declare their own workflows with the orchestrator-core workflow decorators.
These tests verify that the parts compose into well-formed workflows without
needing a database.
"""

import uuid
from functools import partial

import pytest

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import Workflow, begin
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow, modify_workflow, terminate_workflow, validate_workflow
from orchestrator.optical.products.product_types.optical_coherent_pluggable import OpticalCoherentPluggable
from orchestrator.optical.products.product_types.optical_node.nokia_flexils import OpticalNodeNokiaFlexIls
from orchestrator.optical.workflows.optical_coherent_pluggable.create import (
    CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS,
    construct_optical_coherent_pluggable_subscription,
    create_optical_coherent_pluggable_form_generator,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.modify import (
    MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS,
    modify_optical_coherent_pluggable_form_generator,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.shared import (
    load_optical_coherent_pluggable_block,
    update_optical_coherent_pluggable_subscription_description,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.terminate import (
    OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.terminate import (
    terminate_initial_input_form_generator as coherent_pluggable_terminate_initial_input_form_generator,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.validate import (
    OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS,
)
from orchestrator.optical.workflows.optical_node.nokia_flexils.create import (
    CREATE_NOKIA_FLEXILS_BLOCK_STEPS,
    construct_optical_node_nokia_flexils_subscription,
    create_optical_node_nokia_flexils_form_generator,
)
from orchestrator.optical.workflows.optical_node.nokia_flexils.modify import (
    MODIFY_NOKIA_FLEXILS_BLOCK_STEPS,
    modify_optical_node_nokia_flexils_form_generator,
)
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_NODE_TERMINATE_STEPS,
    VALIDATE_OPTICAL_NODE_BLOCK_STEPS,
    load_optical_node_block,
    terminate_initial_input_form_generator,
    terminate_optical_node_form_pages,
)
from orchestrator.optical.workflows.shared import merge_summary_fields


def test_shipped_type_create_workflow_composition() -> None:
    @create_workflow(
        initial_input_form=partial(create_optical_node_nokia_flexils_form_generator, product_name="Nokia FlexILS")
    )
    def create_optical_node_nokia_flexils():
        return (
            begin
            >> construct_optical_node_nokia_flexils_subscription
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> CREATE_NOKIA_FLEXILS_BLOCK_STEPS
            >> store_process_subscription()
        )

    workflow: Workflow = create_optical_node_nokia_flexils
    assert workflow.name == "create_optical_node_nokia_flexils"
    names = [step.name for step in workflow.steps]
    assert names.index("Construct Subscription model") < names.index("Set subscription to 'provisioning'")
    assert names.index("Set subscription to 'provisioning'") < names.index("Retrieve node role and software version")
    assert names.index("Retrieve node role and software version") < names.index("Persist optical node block")
    assert names.index("Construct Subscription model") < names.index("Create Process Subscription relation")


def test_shipped_type_modify_workflow_composition() -> None:
    @modify_workflow(
        initial_input_form=partial(
            modify_optical_node_nokia_flexils_form_generator,
            subscription_model=OpticalNodeNokiaFlexIls,
        )
    )
    def modify_optical_node_nokia_flexils():
        return (
            begin
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> load_optical_node_block
            >> MODIFY_NOKIA_FLEXILS_BLOCK_STEPS
            >> set_status(SubscriptionLifecycle.ACTIVE)
        )

    workflow: Workflow = modify_optical_node_nokia_flexils
    assert workflow.name == "modify_optical_node_nokia_flexils"
    names = [step.name for step in workflow.steps]
    assert names.index("Load optical node block") < names.index("Updating Nokia FlexILS node block")
    assert names.index("Updating Nokia FlexILS node block") < names.index("Persist optical node block")


def test_consumer_model_modify_workflow_composition() -> None:
    from test.test_optical_node_composition import AbstractRouter

    @modify_workflow(
        initial_input_form=partial(
            modify_optical_node_nokia_flexils_form_generator,
            subscription_model=AbstractRouter,
            block_field_name="router",
        )
    )
    def modify_my_router():
        return begin >> MODIFY_NOKIA_FLEXILS_BLOCK_STEPS

    workflow: Workflow = modify_my_router
    assert workflow.name == "modify_my_router"
    names = [step.name for step in workflow.steps]
    assert names.index("Updating Nokia FlexILS node block") < names.index("Persist optical node block")


def test_terminate_and_validate_shared_step_lists_compose() -> None:
    @terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
    def terminate_my_router():
        return begin >> OPTICAL_NODE_TERMINATE_STEPS

    @validate_workflow()
    def validate_my_router():
        return begin >> VALIDATE_OPTICAL_NODE_BLOCK_STEPS

    assert terminate_my_router.name == "terminate_my_router"
    assert validate_my_router.name == "validate_my_router"
    assert "Delete subscription from OSS/BSS" in [step.name for step in terminate_my_router.steps]
    assert "Refresh Optical Node software version" in [step.name for step in validate_my_router.steps]


def test_terminate_form_pages_yield_the_confirmation_page() -> None:
    subscription_id = str(uuid.uuid4())

    generator = terminate_optical_node_form_pages(subscription_id)
    page = next(generator)
    assert issubclass(page, FormPage)
    assert set(page.model_fields) == {"subscription_id"}
    assert page.model_fields["subscription_id"].default == subscription_id


def test_shipped_type_coherent_pluggable_create_workflow_composition() -> None:
    @create_workflow(
        initial_input_form=partial(
            create_optical_coherent_pluggable_form_generator,
            product_name="Coherent Pluggable",
        )
    )
    def create_optical_coherent_pluggable():
        return (
            begin
            >> construct_optical_coherent_pluggable_subscription
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS
            >> update_optical_coherent_pluggable_subscription_description
            >> store_process_subscription()
        )

    workflow: Workflow = create_optical_coherent_pluggable
    assert workflow.name == "create_optical_coherent_pluggable"
    names = [step.name for step in workflow.steps]
    assert names.index("Construct Subscription model") < names.index("Set subscription to 'provisioning'")
    assert names.index("Set subscription to 'provisioning'") < names.index("Persist optical coherent pluggable block")
    assert names.index("Persist optical coherent pluggable block") < names.index("Updating subscription description")
    assert names.index("Construct Subscription model") < names.index("Create Process Subscription relation")


def test_shipped_type_coherent_pluggable_modify_workflow_composition() -> None:
    @modify_workflow(
        initial_input_form=partial(
            modify_optical_coherent_pluggable_form_generator,
            subscription_model=OpticalCoherentPluggable,
        )
    )
    def modify_optical_coherent_pluggable():
        return (
            begin
            >> set_status(SubscriptionLifecycle.PROVISIONING)
            >> load_optical_coherent_pluggable_block
            >> MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS
            >> set_status(SubscriptionLifecycle.ACTIVE)
        )

    workflow: Workflow = modify_optical_coherent_pluggable
    assert workflow.name == "modify_optical_coherent_pluggable"
    names = [step.name for step in workflow.steps]
    assert names.index("Load optical coherent pluggable block") < names.index(
        "Updating Optical Coherent Pluggable block"
    )
    assert names.index("Updating Optical Coherent Pluggable block") < names.index(
        "Persist optical coherent pluggable block"
    )


def test_consumer_model_coherent_pluggable_modify_workflow_composition() -> None:
    from test.test_optical_coherent_pluggable_composition import AbstractRouter

    @modify_workflow(
        initial_input_form=partial(
            modify_optical_coherent_pluggable_form_generator,
            subscription_model=AbstractRouter,
            block_field_name="router",
        )
    )
    def modify_my_router():
        return begin >> MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS

    workflow: Workflow = modify_my_router
    assert workflow.name == "modify_my_router"
    names = [step.name for step in workflow.steps]
    assert names.index("Updating Optical Coherent Pluggable block") < names.index(
        "Persist optical coherent pluggable block"
    )


def test_coherent_pluggable_terminate_and_validate_shared_step_lists_compose() -> None:
    @terminate_workflow(initial_input_form=coherent_pluggable_terminate_initial_input_form_generator)
    def terminate_my_pluggable():
        return begin >> OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS

    @validate_workflow()
    def validate_my_pluggable():
        return begin >> OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS

    assert terminate_my_pluggable.name == "terminate_my_pluggable"
    assert validate_my_pluggable.name == "validate_my_pluggable"
    assert "Deprovision Optical Coherent Pluggable" in [step.name for step in terminate_my_pluggable.steps]
    assert "Load initial state" in [step.name for step in validate_my_pluggable.steps]


def test_merge_summary_fields_appends_and_validates_names() -> None:
    user_input = {"a": 1, "b": 2}
    assert merge_summary_fields(["a"], ["b"], user_input) == ["a", "b"]

    with pytest.raises(ValueError, match="extra_summary_fields"):
        merge_summary_fields(["a"], ["unknown"], user_input)
