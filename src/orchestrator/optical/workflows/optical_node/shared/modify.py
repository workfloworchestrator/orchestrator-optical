"""Shared modification steps for Optical Nodes."""

from collections.abc import Callable, Sequence
from typing import Annotated, Any

from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.workflow import step
from orchestrator.optical.db import location_block_from_subscription
from orchestrator.optical.products.product_blocks.optical_node.abstracts import AbstractOpticalNodeBlockInactive
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_location.shared import active_location_subscription_selector
from orchestrator.optical.workflows.optical_node.shared.create import (
    OPTICAL_NODE_BLOCK_STATE_KEY,
    _optical_node_block_of_subscription,
    optical_node_subscription_description,
    validate_management_ips_uniqueness,
    validate_pqdn_uniqueness,
)
from orchestrator.optical.workflows.shared import merge_summary_fields, summary_form

DEFAULT_INSTRUCTION = "Modify the fields you want to change. Unchanged fields will remain intact."
Instruction = Annotated[
    str,
    Field(title="Instruction", json_schema_extra={"disabled": True}),
]


def update_optical_node_block_fields(
    optical_node_block: Any,
    location_id: UUIDstr,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
) -> None:
    """Update the common Optical Node block fields and keep the node in sync with the location.

    The block is intentionally untyped: the abstract Optical Node block does
    not declare the fields populated here (they are vendor-specific), and the
    helper is shared by all vendors and their consumers.
    """
    optical_node_block.location = location_block_from_subscription(location_id)
    optical_node_block.pqdn = pqdn
    optical_node_block.optical_management_ip = optical_management_ip
    optical_node_block.optical_loopback_ip = optical_loopback_ip


def optical_node_modify_input_form(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel],
    block_field_name: str = "optical_node",
    ip_field_names: tuple[str, ...] = ("optical_management_ip", "optical_loopback_ip"),
    extra_fields: dict[str, tuple[Any, str]] | None = None,
    validate_extra: Callable[..., None] | None = None,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Node subscription.

    The form is prefilled with the current values of the subscription, so unchanged
    fields remain intact. Uniqueness of the PQDN and the management/loopback IPs is
    validated while excluding the subscription being modified.

    Args:
        subscription_id: Subscription id of the Optical Node subscription to modify.
        subscription_model: The ACTIVE subscription model class of the Optical Node product.
        block_field_name: Name of the attribute of the subscription model holding the
            Optical Node block. Consumers that compose the shipped block under a
            different attribute name pass their own attribute name here.
        ip_field_names: Names of the form fields holding IP addresses that must not all be
            empty. Defaults to the two common management/loopback IP fields. Pass an empty
            tuple to skip the check, e.g. when a required vendor-specific field already
            guarantees the invariant.
        extra_fields: Mapping of additional vendor-specific form field names to
            ``(pydantic annotation, block attribute name)`` tuples used to prefill their
            current values. The keys also define their position in the form.
        validate_extra: Optional callback for vendor-specific form validation, receiving
            the form instance and the subscription id being modified.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary; their
            "before" column is left empty, as they have no previous value.

    Yields:
        The dynamic modify form and the summary form, then returns the user input
        together with the loaded subscription.
    """
    location_choice = active_location_subscription_selector()
    subscription = subscription_model.from_subscription(subscription_id)
    node = getattr(subscription, block_field_name)
    customer_choice = customer_choice_selector(include=str(subscription.customer_id))

    fields: dict[str, tuple[Any, Any]] = {
        "instruction": (Instruction, DEFAULT_INSTRUCTION),
        "customer_id": (customer_choice, str(subscription.customer_id)),
        "location_id": (location_choice, str(node.location.owner_subscription_id)),
        "pqdn": (Pqdn, node.pqdn),
        "optical_management_ip": (IPAddress | None, node.optical_management_ip),
        "optical_loopback_ip": (IPAddress | None, node.optical_loopback_ip),
    }
    for field_name, (annotation, block_attribute) in (extra_fields or {}).items():
        fields[field_name] = (annotation, getattr(node, block_attribute))

    def validate_form(self: "ModifyOpticalNodeForm") -> "ModifyOpticalNodeForm":
        validate_pqdn_uniqueness(self.pqdn, exclude_subscription_id=str(subscription.subscription_id))
        validate_management_ips_uniqueness(
            [ip for ip in (self.optical_management_ip, self.optical_loopback_ip) if ip is not None],
            exclude_subscription_id=str(subscription.subscription_id),
        )
        if ip_field_names and not any(getattr(self, name) is not None for name in ip_field_names):
            msg = f"At least one of {', '.join(ip_field_names)} must be provided."
            raise ValueError(msg)
        if validate_extra is not None:
            validate_extra(self, subscription_id=subscription.subscription_id)
        return self

    ModifyOpticalNodeForm = type(  # noqa: N806
        "ModifyOpticalNodeForm",
        (FormPage,),
        {
            "__annotations__": {name: annotation for name, (annotation, _) in fields.items()},
            **{name: default for name, (_, default) in fields.items()},
            "validate_form": model_validator(mode="after")(validate_form),
        },
    )

    user_input = yield ModifyOpticalNodeForm
    user_input_dict = user_input.model_dump()

    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())

    summary_fields = merge_summary_fields(
        [name for name in fields if name != "instruction"],
        extra_summary_fields,
        user_input_dict,
    )
    before = []
    for name in summary_fields:
        if name == "location_id":
            value = node.location.owner_subscription_id
        elif name == "customer_id":
            value = str(subscription.customer_id)
        elif hasattr(node, name):
            value = getattr(node, name)
        else:
            value = ""
        before.append(str(value))
    after = [str(user_input_dict[name]) for name in summary_fields]
    yield from summary_form(
        subscription.product.name,
        {
            "labels": summary_fields,
            "headers": ["Before", "After"],
            "columns": [before, after],
        },
    )

    return user_input_dict | {"subscription": subscription}


@step("Load optical node block")
def load_optical_node_block(subscription: SubscriptionModel) -> State:
    """Put the Optical Node block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_node`` attribute: it makes the block
    available to the shipped block steps under ``OPTICAL_NODE_BLOCK_STATE_KEY``.
    Consumers that compose the shipped block under a different attribute name
    write their own one-step wiring instead.

    Args:
        subscription: The Optical Node subscription.

    Returns:
        The state with the block under the ``optical_node_block`` key.

    Raises:
        ValueError: If the subscription has no Optical Node block under the
            ``optical_node`` attribute.
    """
    return {OPTICAL_NODE_BLOCK_STATE_KEY: _optical_node_block_of_subscription(subscription)}


@step("Updating subscription description")
def update_optical_node_subscription_description(
    subscription: SubscriptionModel,
    optical_node_block: AbstractOpticalNodeBlockInactive | None = None,
) -> State:
    """Update the description of the Optical Node subscription.

    The block is read from the ``optical_node_block`` state key when present
    (e.g. when the shipped block steps ran against a consumer-owned block);
    otherwise it falls back to the ``optical_node`` attribute of the shipped
    subscription models.

    Args:
        subscription: The Optical Node subscription.
        optical_node_block: The Optical Node block of the subscription, when it
            is available in the state under ``OPTICAL_NODE_BLOCK_STATE_KEY``.
    """
    subscription.description = optical_node_subscription_description(subscription, optical_node_block)
    return {"subscription": subscription}


@step("Persist optical node block")
def save_optical_node_block(
    subscription: SubscriptionModel,
    optical_node_block: AbstractOpticalNodeBlockInactive,
) -> State:
    """Persist the Optical Node block found in the state to the database.

    Workflow steps reload the subscription from the database on every step, so
    mutations made on the block in the state are lost unless the block is
    persisted explicitly. This step saves the block tree of the loaded
    subscription (any consumer subscription model that has-a the block works)
    and returns the block, so it can be composed by any consumer workflow.

    Args:
        subscription: The subscription owning the block.
        optical_node_block: The Optical Node block to persist.

    Returns:
        The state with the block under the ``optical_node_block`` key.
    """
    optical_node_block.save(subscription_id=subscription.subscription_id, status=subscription.status)
    return {OPTICAL_NODE_BLOCK_STATE_KEY: optical_node_block}
