"""Composition contract tests for the Optical Node workflow parts.

These tests are database-free: they verify the composition contract itself
(class definition, lifecycle pairing, field classification, the state key
contract of the shipped block steps and the block population logic), not the
workflow execution.
"""

import inspect
import uuid
from types import SimpleNamespace
from typing import Any, cast, get_args

import pytest

from orchestrator.core.domain.base import ProductBlockModel, SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.utils.state import inject_args
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockProvisioning,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlock,
    NokiaFlexIlsBlockInactive,
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node_management import (
    OpticalModuleNodeManagementBlockInactive,
    OpticalModuleNodeManagementBlockProvisioning,
    Platform,
    Vendor,
)
from orchestrator.optical.workflows.optical_node.nokia_flexils.create import (
    CREATE_NOKIA_FLEXILS_BLOCK_STEPS,
    populate_optical_node_nokia_flexils_block,
)
from orchestrator.optical.workflows.optical_node.nokia_flexils.modify import MODIFY_NOKIA_FLEXILS_BLOCK_STEPS
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    OPTICAL_NODE_TERMINATE_STEPS,
    OPTICAL_NODE_VALIDATE_STEPS,
    retrieve,
)
from orchestrator.optical.workflows.optical_node.shared import create as shared_create
from orchestrator.optical.workflows.optical_node.shared.modify import load_optical_node_block
from orchestrator.optical.workflows.optical_node.shared.retrieve import (
    retrieve_optical_node_role_and_software_version,
)


class RouterBlockInactive(ProductBlockModel, product_block_name="TestRouterBlock"):
    """Consumer-style product block with a has-a relation to the shipped Nokia FlexILS block."""

    for_the_optical_module: NokiaFlexIlsBlockInactive


class RouterBlockProvisioning(RouterBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """The provisioning variant of the consumer-style block."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    for_the_optical_module: NokiaFlexIlsBlockProvisioning


class RouterBlock(RouterBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style block."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    for_the_optical_module: NokiaFlexIlsBlock


class AbstractRouterInactive(SubscriptionModel):
    """Abstract consumer-style subscription model composing the block."""

    router: RouterBlockInactive


class AbstractRouterProvisioning(AbstractRouterInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """The provisioning variant of the consumer-style subscription model."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    router: RouterBlockProvisioning


class AbstractRouter(AbstractRouterProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style subscription model."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    router: RouterBlock


BASE_BLOCK_FIELDS = {"name", "label", "subscription_instance_id", "owner_subscription_id"}


@pytest.mark.parametrize(
    ("chain_class", "expected_field_type"),
    [
        (RouterBlockInactive, NokiaFlexIlsBlockInactive),
        (RouterBlockProvisioning, NokiaFlexIlsBlockProvisioning),
        (RouterBlock, NokiaFlexIlsBlock),
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
    return [step.__wrapped__ for step in steps]


@pytest.mark.parametrize(
    "steps",
    [
        CREATE_NOKIA_FLEXILS_BLOCK_STEPS,
        MODIFY_NOKIA_FLEXILS_BLOCK_STEPS,
        OPTICAL_NODE_TERMINATE_STEPS,
        OPTICAL_NODE_VALIDATE_STEPS,
    ],
)
def test_shipped_block_step_lists_are_non_empty(steps) -> None:
    assert len(steps) > 0


@pytest.mark.parametrize("steps", [CREATE_NOKIA_FLEXILS_BLOCK_STEPS, MODIFY_NOKIA_FLEXILS_BLOCK_STEPS])
def test_block_steps_consume_the_block_state_key(steps) -> None:
    for step_func in _step_functions(steps):
        signature = inspect.signature(step_func)
        assert OPTICAL_MODULE_BLOCK_STATE_KEY in signature.parameters


def test_shared_step_lists_are_block_agnostic() -> None:
    for step_func in _step_functions(OPTICAL_NODE_TERMINATE_STEPS + OPTICAL_NODE_VALIDATE_STEPS):
        signature = inspect.signature(step_func)
        assert OPTICAL_MODULE_BLOCK_STATE_KEY not in signature.parameters or (
            signature.parameters[OPTICAL_MODULE_BLOCK_STATE_KEY].default is None
        )


def _make_flexils_block() -> NokiaFlexIlsBlockInactive:
    subscription_id = uuid.uuid4()
    return NokiaFlexIlsBlockInactive(
        name="NokiaFlexIlsBlock",
        subscription_instance_id=subscription_id,
        owner_subscription_id=subscription_id,
        management=OpticalModuleNodeManagementBlockInactive(
            name="OpticalModuleNodeManagementBlock",
            subscription_instance_id=uuid.uuid4(),
            owner_subscription_id=subscription_id,
        ),
        location=OpticalModuleLocationBlockInactive(
            name="OpticalModuleLocationBlock",
            subscription_instance_id=uuid.uuid4(),
            owner_subscription_id=subscription_id,
        ),
    )


def _stub_location(_location_id) -> OpticalModuleLocationBlockInactive:
    subscription_id = uuid.uuid4()
    return OpticalModuleLocationBlockInactive(
        name="OpticalModuleLocationBlock",
        subscription_instance_id=uuid.uuid4(),
        owner_subscription_id=subscription_id,
    )


def _make_flexils_block_provisioning() -> NokiaFlexIlsBlockProvisioning:
    """A PROVISIONING FlexILS block with unset role/version (discovered by the retrieval step).

    The block is fully valid (the contract of the shipped block steps) except
    for the role and the software version, which the retrieval step writes:
    blocks re-validate on attribute assignment, so the vendor, platform, FQDN
    and the remaining mandatory fields must be set.
    """
    subscription_id = uuid.uuid4()
    return NokiaFlexIlsBlockProvisioning.model_construct(
        name="NokiaFlexIlsBlock",
        subscription_instance_id=subscription_id,
        owner_subscription_id=subscription_id,
        optical_flexils_gmpls_id="10.0.0.3",
        optical_flexils_target_id="TID-1",
        management=OpticalModuleNodeManagementBlockProvisioning(
            name="OpticalModuleNodeManagementBlock",
            subscription_instance_id=uuid.uuid4(),
            owner_subscription_id=subscription_id,
            optical_module_node_vendor=Vendor.NOKIA,
            optical_module_node_platform=Platform.FLEXILS,
            optical_module_node_software_version=None,
            optical_module_node_fqdn="flex.ba01.example.com",
            optical_module_node_dcn_loopback_ip=None,
            optical_module_node_dcn_interface_ip=None,
        ),
        location=OpticalModuleLocationBlockProvisioning(
            name="OpticalModuleLocationBlock",
            subscription_instance_id=uuid.uuid4(),
            owner_subscription_id=subscription_id,
            longitude="12.4964",
            latitude="41.9028",
            location_code="rom-01",
        ),
    )


def test_populate_optical_node_nokia_flexils_block(monkeypatch) -> None:
    monkeypatch.setattr(shared_create, "location_block_from_subscription", _stub_location)
    block = _make_flexils_block()

    # Role and software version are written by the block-level discovery step,
    # not by populate: pre-set them to simulate a preceding discovery.
    block.optical_node_role = OpticalNodeRole.ROADM
    block.management.optical_module_node_software_version = "9.0"

    populate_optical_node_nokia_flexils_block(
        optical_module_block=block,
        location_id=str(uuid.uuid4()),
        optical_module_node_fqdn="flex.ba01.example.com",
        optical_module_node_dcn_interface_ip="10.0.0.1",
        optical_module_node_dcn_loopback_ip="10.0.0.2",
        optical_flexils_gmpls_id="10.0.0.3",
        optical_flexils_target_id="TID-1",
    )

    assert str(block.management.optical_module_node_fqdn) == "flex.ba01.example.com"
    assert str(block.management.optical_module_node_dcn_interface_ip) == "10.0.0.1"
    assert str(block.management.optical_module_node_dcn_loopback_ip) == "10.0.0.2"
    assert block.management.optical_module_node_vendor == Vendor.NOKIA
    assert block.management.optical_module_node_platform == Platform.FLEXILS
    assert str(block.optical_flexils_gmpls_id) == "10.0.0.3"
    assert block.optical_flexils_target_id == "TID-1"


def test_block_steps_take_the_lifecycle_matching_block_variant() -> None:
    """Every shipped node block step consumes the PROVISIONING variant of the block, never the Inactive one."""
    steps = (*CREATE_NOKIA_FLEXILS_BLOCK_STEPS, *MODIFY_NOKIA_FLEXILS_BLOCK_STEPS)
    for step_obj in steps:
        step_func = _step_functions([step_obj])[0]
        annotation = inspect.signature(step_func).parameters[OPTICAL_MODULE_BLOCK_STATE_KEY].annotation
        members = get_args(annotation) or (annotation,)
        for member in members:
            if isinstance(member, type) and issubclass(member, AbstractOpticalNodeBlock):
                assert issubclass(member, AbstractOpticalNodeBlockProvisioning), (
                    f"{step_obj.name} consumes {member.__name__}, expected the PROVISIONING variant"
                )


def test_retrieve_optical_node_role_and_software_version_writes_to_block(monkeypatch) -> None:
    monkeypatch.setattr(
        retrieve,
        "_retrieve_optical_node_role_and_software_version",
        lambda _: (OpticalNodeRole.ROADM, "9.0"),
    )
    block = _make_flexils_block_provisioning()
    state = {OPTICAL_MODULE_BLOCK_STATE_KEY: block}

    wrapped = inject_args(retrieve_optical_node_role_and_software_version.__wrapped__)  # type: ignore[unresolved-attribute]
    result = wrapped(dict(state))

    assert result[OPTICAL_MODULE_BLOCK_STATE_KEY] is block
    assert block.optical_node_role == OpticalNodeRole.ROADM
    assert block.management.optical_module_node_software_version == "9.0"


@pytest.mark.parametrize(
    "subscription",
    [
        cast(Any, SimpleNamespace()),
        cast(Any, SimpleNamespace(optical_node=None)),
    ],
)
def test_load_optical_node_block_fails_fast_when_subscription_has_no_block(subscription) -> None:
    with pytest.raises(ValueError, match="under attribute 'optical_node'") as exc_info:
        cast(Any, load_optical_node_block).__wrapped__(subscription)

    assert "must have-a" in str(exc_info.value)


def test_load_optical_node_block_returns_block_in_state() -> None:
    block = _make_flexils_block()
    subscription = cast(Any, SimpleNamespace(optical_node=block))

    state = cast(Any, load_optical_node_block).__wrapped__(subscription)

    assert state == {OPTICAL_MODULE_BLOCK_STATE_KEY: block}


def test_optical_node_subscription_description_fails_fast_without_block() -> None:
    subscription = cast(Any, SimpleNamespace())

    with pytest.raises(ValueError, match="must have-a"):
        shared_create.optical_node_subscription_description(subscription)


def test_optical_node_subscription_description_takes_the_explicit_block() -> None:
    block = cast(Any, SimpleNamespace(management=SimpleNamespace(optical_module_node_fqdn="flex.ba01.example.com")))
    subscription = cast(Any, SimpleNamespace(product=SimpleNamespace(name="Nokia FlexILS")))

    expected = "flex.ba01.example.com (Nokia FlexILS)"
    assert shared_create.optical_node_subscription_description(subscription, block) == expected


def test_optical_node_subscription_description_falls_back_to_the_attribute() -> None:
    block = SimpleNamespace(management=SimpleNamespace(optical_module_node_fqdn="flex.ba01.example.com"))
    subscription = cast(Any, SimpleNamespace(product=SimpleNamespace(name="Nokia FlexILS"), optical_node=block))

    assert shared_create.optical_node_subscription_description(subscription) == "flex.ba01.example.com (Nokia FlexILS)"
