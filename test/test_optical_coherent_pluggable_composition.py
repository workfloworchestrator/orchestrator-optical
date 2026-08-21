"""Composition contract tests for the Optical Coherent Pluggable workflow parts.

These tests are database-free: they verify the composition contract itself
(class definition, lifecycle pairing, field classification, the state key
contract of the shipped block steps and the block population logic), not the
workflow execution.
"""

import inspect
import uuid
from typing import Any, cast

import pytest

from orchestrator.core.domain.base import ProductBlockModel, SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
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
from orchestrator.optical.workflows.optical_coherent_pluggable import create as create_parts
from orchestrator.optical.workflows.optical_coherent_pluggable.create import (
    CREATE_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS,
    populate_optical_coherent_pluggable_block,
    populate_optical_coherent_pluggable_block_step,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.modify import (
    MODIFY_OPTICAL_COHERENT_PLUGGABLE_BLOCK_STEPS,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.shared import (
    OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.terminate import (
    OPTICAL_COHERENT_PLUGGABLE_TERMINATE_STEPS,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.validate import (
    OPTICAL_COHERENT_PLUGGABLE_VALIDATE_STEPS,
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


def _step_functions(steps):
    return [cast(Any, step).__wrapped__ for step in steps]


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
            fqdn_subdomain="site",
        ),
    )


def _make_pluggable_block() -> OpticalCoherentPluggableBlockInactive:
    return OpticalCoherentPluggableBlockInactive(
        name="CoherentPluggableBlock",
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=uuid.uuid4(),
        optical_port_host_node=_make_packet_node_block(),
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
