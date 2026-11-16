"""Shared workflow utilities for Optical Pipes.

This module ships the parts shared by the workflows of the family: the state
key under which the shipped Optical Pipe block travels in the workflow state,
the block re-hydration, load, save and update steps, the human-readable
subscription description, and the form-layer selectors and pipe assembly
helpers (``new_pipe_port_block``, ``new_optical_pipe_subscription``). Database
queries live in the neutral ``orchestrator/optical/db.py`` module.
"""

from collections.abc import Callable
from typing import Annotated, Any, TypeVar, cast
from uuid import UUID

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice, choice_list

from orchestrator.core.db import ProductTable, SubscriptionTable, db
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.domain.base import ProductModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import step
from orchestrator.optical.db import (
    node_block_from_instance,
    pipe_instances_by_block_names,
    subscription_instance_values_by_instance_ids_and_resource_type,
    subscription_instances_by_block_types_and_resource_values,
)
from orchestrator.optical.hal.node import retrieve_ports_spectral_occupations
from orchestrator.optical.hal.port import (
    check_fiber_terminating_port,
    configure_termination_when_attaching_new_fiber,
    get_device_ports_by_role,
    get_device_ports_grouped_by_role,
)
from orchestrator.optical.hal.sessions import device_sessions
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    LINE_SYSTEM_ROLES,
    OADM_ROLES,
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import (
    AbstractOpticalPipeBlock,
    AbstractOpticalPipeBlockInactive,
    AbstractOpticalPipeBlockProvisioning,
    OpticalPipeType,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalOlsPortBlockInactive,
    AbstractOpticalPortBlockInactive,
    OpticalPortRole,
)
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.transponder_client import (
    OpticalTransponderClientPortBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_port.transponder_line import (
    OpticalTransponderLinePortBlockInactive,
)
from orchestrator.optical.products.product_types.optical_pipe.abstracts import (
    AbstractOpticalPipeSubscriptionProvisioning,
)
from orchestrator.optical.utils.labels import device_label, endpoint
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import rehydrate_optical_module_block
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_spectrum_service.shared import optical_node_selector_of_roles
from orchestrator.optical.workflows.shared import create_summary_form, modify_summary_form, optical_port_selector

T = TypeVar("T", bound=AbstractOpticalPortBlockInactive)

#: Inactive Optical Port block class for each Optical Port role: the single
#: source of truth for the (port role) -> (port block class) mapping used by the
#: shipped pipe builders.
PORT_BLOCK_CLASS_BY_ROLE: dict[OpticalPortRole, type[AbstractOpticalPortBlockInactive]] = {
    OpticalPortRole.OLS_LINE: OlsLinePortBlockInactive,
    OpticalPortRole.OLS_ADD_DROP: OlsAddDropPortBlockInactive,
    OpticalPortRole.TRANSPONDER_CLIENT: OpticalTransponderClientPortBlockInactive,
    OpticalPortRole.TRANSPONDER_LINE: OpticalTransponderLinePortBlockInactive,
}

#: Optical Node roles any pipe can terminate on: the line-system nodes (FlexILS ROADMs and
#: OLA/OA amplifiers, OADM-capable Groove G30 nodes) plus plain transponders, since a
#: transponder's line port is where a DCI span lands. There is deliberately no separate
#: set for spans: a span runs over the same dark fibre as a patch or a leased spectrum,
#: just with different port roles (see :func:`pipe_port_roles`). Amplifiers stay in,
#: both ROADM↔amplifier and amplifier↔amplifier, being transit segments of longer
#: ROADM-to-ROADM paths. Packet nodes are the only shipped role excluded.
PIPE_NODE_ROLES = [*LINE_SYSTEM_ROLES, OpticalNodeRole.TRANSPONDER]


#: Optical Port roles a pipe type terminates on, per node vendor/platform. A Nokia
#: FlexILS node terminates spans on its OLS line ports and patches / leased spectrum on
#: its OLS add/drop (SCG) ports; a Groove G30 node can terminate a pipe on both its OLS
#: ports (OCC2 cards) and its transponder ports. A GX G42 node exposes transceiver ports
#: only (see :func:`orchestrator.optical.hal.port.get_device_ports_by_role`), so every pipe
#: lands on one of those: a DCI span runs straight between two transceiver line ports.
_PIPE_PORT_ROLES: dict[tuple[Vendor, Platform], dict[OpticalPipeType, list[OpticalPortRole]]] = {
    (Vendor.NOKIA, Platform.FLEXILS): {
        OpticalPipeType.SPAN: [OpticalPortRole.OLS_LINE],
        OpticalPipeType.PATCH: [OpticalPortRole.OLS_ADD_DROP],
        OpticalPipeType.LEASED_SPECTRUM: [OpticalPortRole.OLS_ADD_DROP, OpticalPortRole.OLS_LINE],
    },
    (Vendor.NOKIA, Platform.GROOVE_G30): {
        OpticalPipeType.SPAN: [OpticalPortRole.OLS_LINE, OpticalPortRole.TRANSPONDER_LINE],
        OpticalPipeType.PATCH: [
            OpticalPortRole.OLS_ADD_DROP,
            OpticalPortRole.TRANSPONDER_CLIENT,
            OpticalPortRole.TRANSPONDER_LINE,
        ],
        OpticalPipeType.LEASED_SPECTRUM: [
            OpticalPortRole.OLS_ADD_DROP,
            OpticalPortRole.OLS_LINE,
            OpticalPortRole.TRANSPONDER_LINE,
        ],
    },
    (Vendor.NOKIA, Platform.GX_G42): {
        OpticalPipeType.SPAN: [OpticalPortRole.TRANSPONDER_LINE],
        OpticalPipeType.PATCH: [OpticalPortRole.TRANSPONDER_CLIENT, OpticalPortRole.TRANSPONDER_LINE],
        OpticalPipeType.LEASED_SPECTRUM: [OpticalPortRole.TRANSPONDER_LINE],
    },
}

#: Fallback for a vendor/platform without an entry above: a transponder-like node, whose
#: line port is where a span or a leased spectrum lands and whose client ports take patches.
_DEFAULT_PIPE_PORT_ROLES: dict[OpticalPipeType, list[OpticalPortRole]] = {
    OpticalPipeType.SPAN: [OpticalPortRole.OLS_LINE, OpticalPortRole.TRANSPONDER_LINE],
    OpticalPipeType.PATCH: [OpticalPortRole.TRANSPONDER_CLIENT, OpticalPortRole.TRANSPONDER_LINE],
    OpticalPipeType.LEASED_SPECTRUM: [OpticalPortRole.TRANSPONDER_LINE],
}


def pipe_port_roles(
    pipe_type: OpticalPipeType,
    node_block: AnyOpticalNodeBlockProvisioningUnion,
) -> list[OpticalPortRole]:
    """Return the Optical Port roles a pipe type can terminate on the given node.

    The roles depend on both the pipe type and the node's vendor/platform (see
    :data:`_PIPE_PORT_ROLES`). The returned roles are the subset of the pipe block union
    (see ``optical_port/unions.py``) that the node can expose, so they can be requested as
    they are from :func:`orchestrator.optical.hal.port.get_device_ports_by_role`.

    Args:
        pipe_type: The type of the Optical Pipe.
        node_block: The Optical Node hosting the termination.

    Returns:
        The Optical Port roles the pipe can terminate on the node.

    Raises:
        ValueError: If the pipe type is not supported.
    """
    vendor_platform = (
        node_block.management.optical_module_node_vendor,
        node_block.management.optical_module_node_platform,
    )
    roles = _PIPE_PORT_ROLES.get(vendor_platform, _DEFAULT_PIPE_PORT_ROLES).get(pipe_type)
    if roles is None:
        msg = f"Unsupported optical pipe type: {pipe_type.value}"
        raise ValueError(msg)
    return list(roles)


def get_pipe_ports(
    node_block: AnyOpticalNodeBlockProvisioningUnion,
    roles: list[OpticalPortRole],
) -> list[str]:
    """Return the device port names of a node for the given Optical Port roles.

    This is the single seam the pipe forms and builders use to discover the device
    ports of a pipe's terminations: a thin wrapper over the HAL role-based
    enumeration (:func:`orchestrator.optical.hal.port.get_device_ports_by_role`).
    """
    return get_device_ports_by_role(node_block, roles)


def resolve_port_role(
    node_block: AnyOpticalNodeBlockProvisioningUnion,
    port_name: str,
    roles: list[OpticalPortRole],
) -> OpticalPortRole:
    """Return the Optical Port role of a node port, among the given roles.

    Args:
        node_block: The Optical Node hosting the port.
        port_name: The device name of the port.
        roles: The roles the port is expected to have (the pipe's roles on the node).

    Returns:
        The Optical Port role of the port.

    Raises:
        ValueError: If the port is not one of the given roles on the node, or if
            it matches more than one of them (the device roles must be disjoint).
    """
    # One enumeration for all the roles: asking role by role repeats the device reads.
    ports_by_role = get_device_ports_grouped_by_role(node_block, roles)
    matching_roles = [role for role, port_names in ports_by_role.items() if port_name in port_names]
    if len(matching_roles) == 1:
        return matching_roles[0]
    if len(matching_roles) > 1:
        msg = (
            f"Port {port_name} matches multiple roles {[r.value for r in matching_roles]} on "
            f"{node_block.management.optical_module_node_name}"
        )
        raise ValueError(msg)
    msg = (
        f"Port {port_name} is not one of the roles {[r.value for r in roles]} on "
        f"{node_block.management.optical_module_node_name}"
    )
    raise ValueError(msg)


def optical_pipe_subscription_description(
    subscription: AbstractOpticalPipeSubscriptionProvisioning,
    optical_module_block: AbstractOpticalPipeBlockInactive | None = None,
) -> str:
    """Generate the human-readable description of an Optical Pipe subscription.

    The description is derived from the pipe name and the product name, so the
    same function can be reused by consumers that compose the shipped block
    under their own attribute: pass the shipped block explicitly, otherwise it
    falls back to the ``optical_pipe`` attribute of the shipped subscription
    models.

    Args:
        subscription: The Optical Pipe subscription.
        optical_module_block: The Optical Pipe block of the subscription. When
            given, it is used instead of the ``optical_pipe`` attribute of the
            shipped subscription models.

    Returns:
        The subscription description, e.g. ``"OF-778812 flex.a 1-3-L1 <-> flex.b 1-4-L1"``: the
        name when the user gave one, then the two ends (the product name is already a column
        of the subscription list). The two ends alone when the pipe has the default name.

    Raises:
        ValueError: If the subscription has no Optical Pipe block under the
            ``optical_pipe`` attribute and no block was passed.
    """
    pipe = optical_module_block or subscription.optical_pipe
    port_a, port_b, name = _pipe_ends_and_user_name(pipe)
    ends = (
        f"{endpoint(port_a.optical_port_host_node, port_a.optical_port_name)}"
        f" <-> {endpoint(port_b.optical_port_host_node, port_b.optical_port_name)}"
    )
    return f"{name} {ends}" if name else ends


def optical_pipe_block_from_state(
    optical_module_block: AbstractOpticalPipeBlockProvisioning | dict[str, Any] | None,
) -> AbstractOpticalPipeBlockProvisioning:
    """Return the Optical Pipe block of the workflow state as a domain model.

    Workflow steps execute with the state serialized between steps, so a block
    passed under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` arrives as a plain dict
    (its serialized form, carrying the full block data) rather than as a domain
    model. This helper returns the value unchanged when it is already a domain
    model (in-process usage, e.g. in tests) and reconstructs the block from the
    serialized data otherwise. The concrete block chain is resolved by its
    ``product_block_name`` and its lifecycle variant from the status of its
    owner subscription, so blocks of any lifecycle are loaded as their matching
    variant (INITIAL, PROVISIONING or ACTIVE).

    Args:
        optical_module_block: The block value from the workflow state, or None.

    Returns:
        The Optical Pipe block as a domain model, or None when the value is None.

    Raises:
        ValueError: If the block in the state has no ``subscription_instance_id``.
    """
    if optical_module_block is None:
        msg = "No Optical Pipe block in the state under OPTICAL_MODULE_BLOCK_STATE_KEY"
        raise ValueError(msg)
    if isinstance(optical_module_block, AbstractOpticalPipeBlockProvisioning):
        return optical_module_block
    return _optical_pipe_block_from_state(optical_module_block)


def _optical_pipe_block_from_state(optical_module_block: dict[str, Any]) -> AbstractOpticalPipeBlockProvisioning:
    """Reconstruct an Optical Pipe block from its serialized form.

    Thin wrapper around the family-agnostic re-hydration
    (:func:`orchestrator.optical.workflows.block.rehydrate_optical_module_block`),
    kept for the narrowed return type and the family-specific error message.

    Args:
        optical_module_block: The serialized block from the workflow state.

    Returns:
        The Optical Pipe block as a domain model.

    Raises:
        ValueError: If the block in the state has no ``subscription_instance_id``,
            or if no subscription instance exists with the given id.
    """
    return cast(
        AbstractOpticalPipeBlockProvisioning,
        rehydrate_optical_module_block(optical_module_block, block_description="Optical Pipe"),
    )


@step("Load optical pipe block")
def load_optical_pipe_block(subscription: AbstractOpticalPipeSubscriptionProvisioning) -> State:
    """Put the Optical Pipe block of the subscription in the state.

    This is the thin wiring step for the shipped subscription product types,
    whose block lives under the ``optical_pipe`` attribute: it makes the block
    available to the shipped block steps under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    Consumers that compose the shipped block under a different attribute name
    write their own one-step wiring instead.

    Args:
        subscription: The Optical Pipe subscription.

    Returns:
        The state with the block under the ``optical_module_block`` key.

    Raises:
        ValueError: If the subscription has no Optical Pipe block under the
            ``optical_pipe`` attribute.
    """
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: subscription.optical_pipe}


@step("Configure Optical Pipe Terminations")
@device_sessions()
def configure_pipe_terminations(
    optical_module_block: AbstractOpticalPipeBlockProvisioning,
) -> State:
    """Configure the terminating ports of an optical pipe on the devices.

    Operates only on the Optical Pipe block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``, the same block the rest of the shipped
    block steps act on. The block is re-hydrated from its serialized form (see
    :func:`optical_pipe_block_from_state`); it is read-only here, so only the
    device configuration results are returned. When one of the two host nodes
    is a Nokia FlexILS and the other is not, the FlexILS side is configured
    first: its configuration references the remote node.

    Args:
        optical_module_block: The Optical Pipe block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Raises:
        TypeError: If a termination is not hosted on an Optical Node.
    """
    pipe_block = optical_pipe_block_from_state(optical_module_block)
    terminations = pipe_block.optical_pipe_terminations
    port_a, port_b = terminations
    host_node_a = port_a.optical_port_host_node
    host_node_b = port_b.optical_port_host_node
    if not isinstance(host_node_a, AbstractOpticalNodeBlockInactive) or not isinstance(
        host_node_b, AbstractOpticalNodeBlockInactive
    ):
        msg = "Optical pipe terminations must be hosted on Optical Module's Nodes"
        raise TypeError(msg)
    if (
        host_node_b.management.optical_module_node_vendor,
        host_node_b.management.optical_module_node_platform,
    ) == (Vendor.NOKIA, Platform.FLEXILS) and (
        host_node_a.management.optical_module_node_vendor,
        host_node_a.management.optical_module_node_platform,
    ) != (Vendor.NOKIA, Platform.FLEXILS):
        # Configure the FlexILS side first: its configuration references the remote node.
        port_a, port_b = port_b, port_a

    pipe_type = pipe_block.optical_pipe_type
    configuration_results = {
        f"{port_a.optical_port_host_node.management.optical_module_node_name} {port_a.optical_port_name}": (
            configure_termination_when_attaching_new_fiber(
                port_a, port_b, pipe_type, label=pipe_termination_label(pipe_block, port_b)
            )
        ),
        f"{port_b.optical_port_host_node.management.optical_module_node_name} {port_b.optical_port_name}": (
            configure_termination_when_attaching_new_fiber(
                port_b, port_a, pipe_type, label=pipe_termination_label(pipe_block, port_a)
            )
        ),
    }
    return {"configuration_results": configuration_results, OPTICAL_MODULE_BLOCK_STATE_KEY: pipe_block}


@step("Check Optical Pipe Terminations")
@device_sessions()
def check_pipe_terminations(optical_module_block: AbstractOpticalPipeBlockProvisioning) -> State:
    """Verify that the terminating ports of an optical pipe are correctly configured.

    Operates only on the Optical Pipe block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY`` (the same block the rest of the shipped
    block steps act on): it re-hydrates the block and checks both terminations
    against their remote end. This is the read-only device check shared by the
    shipped validate and reconcile workflows of every pipe family (fiber span,
    fiber patch and leased spectrum).

    Args:
        optical_module_block: The Optical Pipe block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

    Raises:
        ValueError: If a termination's configuration does not match the expected one.
        UnsupportedPlatformError: If a host node is not supported by this operation.
    """
    pipe_block = optical_pipe_block_from_state(optical_module_block)
    port_a, port_b = pipe_block.optical_pipe_terminations
    pipe_type = pipe_block.optical_pipe_type
    check_fiber_terminating_port(port_a, port_b, pipe_type, label=pipe_termination_label(pipe_block, port_b))
    check_fiber_terminating_port(port_b, port_a, pipe_type, label=pipe_termination_label(pipe_block, port_a))
    return {}


@step("Updating Optical Pipe block")
def update_optical_pipe_block(
    optical_module_block: AbstractOpticalPipeBlockProvisioning,
    optical_pipe_name: str,
) -> State:
    """Update the Optical Pipe block in the state from the modify-form keys.

    Only the ``optical_pipe_name`` is written to the block: the shipped modify
    block steps never persist a changed ``customer_id`` (the form still emits
    it; add your own step if your product tracks it). Workflow steps execute
    with the state serialized between steps, so the block is re-hydrated from
    the database by its ``subscription_instance_id`` before it is updated.

    Args:
        optical_module_block: The Optical Pipe block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY`` (the provisioning variant, while
            the subscription is being modified).
        optical_pipe_name: The new name of the pipe.

    Raises:
        ValueError: If there is no Optical Pipe block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    pipe_block = optical_pipe_block_from_state(optical_module_block)
    pipe_block.optical_pipe_name = optical_pipe_name
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: pipe_block}


@step("Set Optical Pipe subscription description")
def set_optical_pipe_subscription_description(
    subscription: AbstractOpticalPipeSubscriptionProvisioning,
    optical_module_block: AbstractOpticalPipeBlockProvisioning | None = None,
) -> State:
    """Set the description of the Optical Pipe subscription.

    The block is read from the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``
    (put there by the construct step of the shipped create workflows or by
    :func:`load_optical_pipe_block` in the shipped modify/validate/terminate
    workflows); a step chain must always load the block into the state before
    this step runs.

    Args:
        subscription: The Optical Pipe subscription.
        optical_module_block: The Optical Pipe block of the subscription, as
            available in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    pipe = optical_pipe_block_from_state(optical_module_block)
    subscription.description = optical_pipe_subscription_description(subscription, pipe)
    return {"subscription": subscription, "subscription_description": subscription.description}


@step("Retrieve Used Passbands")
@device_sessions()
def retrieve_optical_pipe_used_passbands(
    optical_module_block: AbstractOpticalPipeBlockProvisioning,
) -> State:
    """Refresh the passbands in use on the Open Line System terminating ports.

    Operates only on the Optical Pipe block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``, the same block the rest of the shipped
    block steps act on. Only the OLS terminating ports (the ones that carry
    ``optical_passbands``) hosted on an add/drop multiplexer (see ``OADM_ROLES``) are
    refreshed from the devices; every other termination (e.g. transponder ports) is
    left untouched, so the step is a no-op for pipes
    whose terminations are all transponder ports. Callers persist the refreshed
    passbands with :func:`orchestrator.optical.workflows.block.save_optical_module_block`.
    """
    pipe_block = optical_pipe_block_from_state(optical_module_block)
    terminations = pipe_block.optical_pipe_terminations
    for port in terminations:
        if not isinstance(port, AbstractOpticalOlsPortBlockInactive):
            continue
        host_node = port.optical_port_host_node
        if host_node.optical_node_role not in OADM_ROLES:
            continue
        if port.optical_port_name is None:
            msg = f"Optical port block of {host_node.management.optical_module_node_name} has no port name"
            raise ValueError(msg)
        port.optical_passbands = retrieve_ports_spectral_occupations(host_node).get(port.optical_port_name, [])
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: pipe_block}


def optical_pipe_selector(
    prompt: str | None = None, *, pipe_types: list[OpticalPipeType] | None = None
) -> type[Choice]:
    """Create a Choice selector for active optical pipe blocks.

    Block-based selector: option values are pipe block subscription instance ids and
    labels are the stored pipe names, so consumers composing the shipped blocks
    under their own product types are covered. No block is loaded: instances are
    enumerated by block name (filtered by pipe type in the database query when
    requested) and labels are read from the stored resource values in two queries
    total,     however many pipes exist.

    Args:
        prompt: Prompt of the selector.
        pipe_types: Pipe types to offer; None or empty (default) offers all
            active pipe blocks.
    """
    if pipe_types:
        instances = subscription_instances_by_block_types_and_resource_values(
            set(AbstractOpticalPipeBlockInactive.__names__),
            {"optical_pipe_type": [pipe_type.value for pipe_type in pipe_types]},
            [SubscriptionLifecycle.ACTIVE],
        )
    else:
        instances = pipe_instances_by_block_names(
            set(AbstractOpticalPipeBlockInactive.__names__),
            [SubscriptionLifecycle.ACTIVE],
        )
    names = {
        str(value.subscription_instance_id): str(value.value)
        for value in subscription_instance_values_by_instance_ids_and_resource_type(
            [str(instance.subscription_instance_id) for instance in instances], "optical_pipe_name"
        )
        if value.value
    }
    options = sorted(
        (
            (str(instance.subscription_instance_id), names.get(str(instance.subscription_instance_id), "<unknown>"))
            for instance in instances
        ),
        key=lambda item: item[1],
    )
    products = dict(options)

    if not prompt:
        prompt = "Select an optical pipe"

    dynamic_class = Choice(prompt, zip(products.keys(), products.items(), strict=False))
    return cast(type[Choice], dynamic_class)


def multiple_optical_pipe_selector(
    prompt: str = "Select optical pipes",
    min_items: int = 0,
    max_items: int | None = None,
    *,
    unique_items: bool = True,
    pipe_types: list[OpticalPipeType] | None = None,
) -> type[list[Choice]]:
    """Selector for multiple optical pipe blocks.

    Block-based selector: option values are pipe block subscription instance ids.

    Args:
        prompt: Prompt of the selector.
        min_items: Minimum number of selections required.
        max_items: Maximum number of selections allowed.
        unique_items: Whether duplicate selections are allowed.
        pipe_types: Pipe types to offer; None or empty (default) offers all
            active pipe blocks.

    Returns:
        A ``Choice`` list type for selecting multiple pipes.
    """
    base_choice = optical_pipe_selector(prompt, pipe_types=pipe_types)
    dynamic_class = choice_list(base_choice, min_items=min_items, max_items=max_items, unique_items=unique_items)
    return cast(type[list[Choice]], Annotated[dynamic_class, Field(title=prompt)])


def new_pipe_port_block[T: AbstractOpticalPortBlockInactive](
    subscription_id: UUID,
    host_node_block: AbstractOpticalNodeBlockInactive,
    port_name: str,
    port_block_class: type[T],
) -> T:
    """Create a new Optical Port product block for a pipe termination.

    The host node block comes from an existing Optical Node subscription and is linked
    to the new port block as a foreign instance: saving the port block only records the
    relation to the node and never touches the node subscription itself.

    Args:
        subscription_id: Subscription id of the pipe subscription owning the port block.
        host_node_block: Optical Node block hosting the port.
        port_name: The name of the port on the device.
        port_block_class: The inactive port block class to instantiate.

    Returns:
        The created port block.
    """
    kwargs: dict[str, Any] = {
        "optical_port_name": port_name,
        "optical_port_host_node": host_node_block,
    }
    return port_block_class.new(subscription_id=subscription_id, **kwargs)


def new_optical_pipe_subscription(
    subscription_model: type[SubscriptionModel],
    product_id: UUIDstr,
    customer_id: str,
    pipe_block: AbstractOpticalPipeBlockInactive,
) -> SubscriptionModel:
    """Build a new pipe subscription model around a pre-built pipe block.

    ``from_product_id`` cannot be used for optical pipes: the placeholder terminations
    it creates cannot be validated, because the Optical Port blocks require a host node
    at construction time. The pipe block is therefore built first, with its two
    terminations already in place, and the subscription model is assembled from it.

    Args:
        subscription_model: The inactive subscription model of the pipe product.
        product_id: Id of the pipe product.
        customer_id: Customer (location subscription) id of the pipe.
        pipe_block: The pipe block with its two terminations.

    Returns:
        The new pipe subscription model in the INITIAL state.
    """
    product_db = db.session.get(ProductTable, product_id)
    if product_db is None:
        msg = f"Could not find a product for the given product_id {product_id}"
        raise KeyError(msg)

    product = ProductModel(
        product_id=product_db.product_id,
        name=product_db.name,
        description=product_db.description,
        product_type=product_db.product_type,
        tag=product_db.tag,
        status=product_db.status,
        created_at=product_db.created_at,
        end_date=product_db.end_date,
    )
    description = f"Initial subscription of {product_db.description}"
    subscription_id = pipe_block.owner_subscription_id
    subscription = SubscriptionTable(
        subscription_id=subscription_id,
        product_id=product_id,
        customer_id=customer_id,
        description=description,
        status=SubscriptionLifecycle.INITIAL.value,
        insync=False,
        version=1,
    )
    db.session.add(subscription)

    fixed_inputs = {fixed_input.name: fixed_input.value for fixed_input in product_db.fixed_inputs}
    model_data: dict[str, Any] = {
        "product": product,
        "customer_id": customer_id,
        "subscription_id": subscription_id,
        "description": description,
        "status": SubscriptionLifecycle.INITIAL,
        "insync": False,
        "start_date": None,
        "end_date": None,
        "note": None,
        "version": 1,
        **fixed_inputs,
        "optical_pipe": pipe_block,
    }
    model = subscription_model(**model_data)
    model.db_model = subscription
    return model


def _pipe_ends_and_user_name(pipe_block: Any) -> tuple[Any, Any, str]:
    """Return the two terminations of a pipe and its name without the default identifier."""
    port_a, port_b = pipe_block.optical_pipe_terminations
    default = default_pipe_identifier_of(pipe_block)
    return port_a, port_b, (pipe_block.optical_pipe_name or "").replace(default, "").strip()


def pipe_termination_label(pipe_block: Any, far_port: Any) -> str:
    """Return the label of the pipe termination facing ``far_port``: ``"[<pipe>] > <far node> <far port>"``.

    The pipe name is part of the label only when the user gave one (a circuit id, a
    provider reference): the default identifier only repeats the two ends. The label is
    computed when it is written or checked, so it follows a rename of the pipe or of a node.

    Args:
        pipe_block: The Optical Pipe block, with its two terminations and its name set.
        far_port: The termination at the other end of the pipe.
    """
    _, _, name = _pipe_ends_and_user_name(pipe_block)
    return device_label(name, endpoint(far_port.optical_port_host_node, far_port.optical_port_name))


def default_pipe_identifier(
    node_a_block: AbstractOpticalNodeBlockInactive,
    port_a_name: str,
    node_b_block: AbstractOpticalNodeBlockInactive,
    port_b_name: str,
) -> str:
    """Return the default identifier of a pipe, e.g. ``"nodeA portA --- nodeB portB"``."""
    return (
        f"{node_a_block.management.optical_module_node_name} {port_a_name}"
        f" --- {node_b_block.management.optical_module_node_name} {port_b_name}"
    )


def default_pipe_identifier_of(pipe_block: Any) -> str:
    """Return the default identifier of an existing pipe, from its two terminations."""
    port_a, port_b = pipe_block.optical_pipe_terminations
    return default_pipe_identifier(
        port_a.optical_port_host_node,
        str(port_a.optical_port_name),
        port_b.optical_port_host_node,
        str(port_b.optical_port_name),
    )


def pipe_nodes_form(
    product_name: str,
    node_a_choice: type[Choice],
    node_b_choice: type[Choice],
    *,
    allow_same_node: bool = False,
    require_same_vendor: bool = False,
) -> type[FormPage]:
    """Return the two-nodes FormPage of an Optical Pipe create form.

    This is the first page of the Optical Pipe create form: the two nodes the
    pipe connects. The page title is the product name. By default it validates
    that the two ends of the pipe are on different nodes; a fiber patch may
    instead connect two ports of the same node (``allow_same_node``), and a fiber
    span requires the two nodes to be of the same vendor and platform
    (``require_same_vendor``).

    Args:
        product_name: Name of the product being created, used as the page title.
        node_a_choice: The ``Choice`` selector of the Optical Node blocks of node A.
        node_b_choice: The ``Choice`` selector of the Optical Node blocks of node B.
        allow_same_node: When True, the two ends may be on the same node (fiber patches).
        require_same_vendor: When True, the two nodes must be of the same vendor and platform
            (fiber spans).

    Returns:
        The two-nodes FormPage of the Optical Pipe create form.
    """

    class CreatePipeNodesForm(FormPage):
        model_config = ConfigDict(title=product_name)

        node_a_instance_id: node_a_choice
        node_b_instance_id: node_b_choice

        @model_validator(mode="after")
        def validate_nodes(self) -> "CreatePipeNodesForm":
            if not allow_same_node and self.node_a_instance_id == self.node_b_instance_id:
                msg = "The two ends of the pipe must be on different nodes."
                raise ValueError(msg)
            if require_same_vendor:
                node_a_block = node_block_from_instance(self.node_a_instance_id)
                node_b_block = node_block_from_instance(self.node_b_instance_id)
                if (
                    node_a_block.management.optical_module_node_vendor,
                    node_a_block.management.optical_module_node_platform,
                ) != (
                    node_b_block.management.optical_module_node_vendor,
                    node_b_block.management.optical_module_node_platform,
                ):
                    msg = "A fiber span must connect two nodes of the same vendor and platform."
                    raise ValueError(msg)
            return self

    return CreatePipeNodesForm


def pipe_terminations_form(
    product_name: str,
    port_a_choice: type[Choice],
    port_b_choice: type[Choice],
) -> type[FormPage]:
    """Return the terminations FormPage of an Optical Pipe create form.

    This is the second page of the Optical Pipe create form: the identifier of
    the pipe and the two terminating ports. The identifier is optional: when it
    is left empty, the create page sequence resolves it to the default
    ``"node A port A --- node B port B"``.

    Args:
        product_name: Name of the product being created, used as the page title.
        port_a_choice: The ``Choice`` selector of the unused ports of node A.
        port_b_choice: The ``Choice`` selector of the unused ports of node B.

    Returns:
        The terminations FormPage of the Optical Pipe create form.
    """

    class CreatePipeTerminationsForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Terminations")

        optical_pipe_name: str | None = Field(
            None,
            title="Pipe Identifier",
            description="Unique pipe ID or code. Leave empty to use the default 'node A port A --- node B port B'.",
        )
        port_a_name: port_a_choice
        port_b_name: port_b_choice

    return CreatePipeTerminationsForm


def create_pipe_form_pages(
    product_name: str,
    *,
    pipe_type: OpticalPipeType,
) -> FormGenerator:
    """Yield the FormPages of an Optical Pipe create form, in order.

    This is the shared page sequence of the Optical Pipe create form: it yields
    the two-nodes page and the terminations page, and returns the collected user
    input as a flat dict of the ``optical_*`` state keys, consumed by the shipped
    construct step. The pipe type drives the per-family differences: the node
    endpoints offered (a fiber span only offers line-system nodes (ROADM /
    OADM-capable plus amplifiers) and
    requires the two nodes to be of the same vendor/platform, a fiber patch allows
    the two ends to be on the same node) and the device ports offered as terminations (the pipe's
    Optical Port roles on the node, see :func:`pipe_port_roles`). The terminations
    page is always the shared one. The customer of the subscription is collected
    separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.
        pipe_type: The type of the Optical Pipe being created.

    Returns:
        The collected user input of the shipped pages.
    """
    is_span = pipe_type is OpticalPipeType.SPAN
    is_patch = pipe_type is OpticalPipeType.PATCH

    node_a_choice = optical_node_selector_of_roles(
        PIPE_NODE_ROLES,
        prompt=f"This {product_name.lower()} connects this node:",
    )
    node_b_choice = optical_node_selector_of_roles(PIPE_NODE_ROLES, prompt="...to this other node:")

    user_input_dict: dict[str, Any] = {}
    user_input_dict.update(
        (
            yield pipe_nodes_form(
                product_name,
                node_a_choice,
                node_b_choice,
                allow_same_node=is_patch,
                require_same_vendor=is_span,
            )
        ).model_dump()
    )

    node_a_block = node_block_from_instance(user_input_dict["node_a_instance_id"])
    node_b_block = node_block_from_instance(user_input_dict["node_b_instance_id"])

    port_prompt = "Select an unused port on {name}"
    port_a_choice = optical_port_selector(
        node_a_block,
        pipe_port_roles(pipe_type, node_a_block),
        prompt=port_prompt.format(name=node_a_block.management.optical_module_node_name),
    )
    port_b_choice = optical_port_selector(
        node_b_block,
        pipe_port_roles(pipe_type, node_b_block),
        prompt=port_prompt.format(name=node_b_block.management.optical_module_node_name),
    )
    user_input_dict.update((yield pipe_terminations_form(product_name, port_a_choice, port_b_choice)).model_dump())

    user_input_dict["optical_pipe_name"] = user_input_dict["optical_pipe_name"] or default_pipe_identifier(
        node_a_block, user_input_dict["port_a_name"], node_b_block, user_input_dict["port_b_name"]
    )
    return user_input_dict


def create_optical_pipe_form_generator(
    product_name: str,
    create_pages: Callable[[str], FormGenerator],
    summary_fields: list[str],
) -> FormGenerator:
    """Generate the initial input form for creating an Optical Pipe.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    construct step. It is a thin composition of the customer page, the create
    page sequence of the pipe family and the summary form.

    Args:
        product_name: Name of the product being created.
        create_pages: The create page sequence of the pipe family.
        summary_fields: The field names to display in the summary form.
    """
    user_input_dict = yield from customer_choice_form_page(title=product_name)
    user_input_dict.update((yield from create_pages(product_name)))
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
    return user_input_dict


def modify_optical_pipe_form(pipe: AbstractOpticalPipeBlock) -> type[FormPage]:
    """Return the modify FormPage of an Optical Pipe subscription.

    The page is prefilled with the current ``optical_pipe_name`` of the
    block, so unchanged fields remain intact. The name may be left empty to
    go back to the default identifier (see :func:`modify_optical_pipe_form_pages`).

    Args:
        pipe: The Optical Pipe block being modified.

    Returns:
        The prefilled modify FormPage of the shipped modify form.
    """

    class ModifyOpticalPipeForm(FormPage):
        optical_pipe_name: str | None = Field(
            pipe.optical_pipe_name,
            title="Pipe Identifier",
            description="Unique pipe ID or code. Leave empty to use the default 'node A port A --- node B port B'.",
        )

    return ModifyOpticalPipeForm


def modify_optical_pipe_form_pages(pipe: AbstractOpticalPipeBlock) -> FormGenerator:
    """Yield the FormPage of an Optical Pipe modify form.

    This is the shipped modify form as a page sequence: it yields the prefilled
    modify page and returns the collected user input as a flat dict of the
    ``optical_*`` state keys, consumed by the shipped modify steps. A name left
    empty (or blank) becomes the default identifier of the pipe, as on the
    create form. The customer of the subscription is collected separately by
    the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        pipe: The Optical Pipe block being modified.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input_dict = (yield modify_optical_pipe_form(pipe)).model_dump()
    name = (user_input_dict["optical_pipe_name"] or "").strip()
    user_input_dict["optical_pipe_name"] = name or default_pipe_identifier_of(pipe)
    return user_input_dict


def modify_optical_pipe_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel],
    block_field_name: str = "optical_pipe",
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Pipe subscription.

    The form is prefilled with the current values of the block, so
    unchanged fields remain intact. It is a thin composition of the customer
    page, the modify page sequence and the summary form. Shipped-product only:
    consumers compose their own form generator from the shipped page sequence.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical
            Pipe product.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Pipe block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    pipe = getattr(subscription, block_field_name)

    user_input_dict = yield from customer_choice_form_page(include=subscription.customer_id)
    user_input_dict.update((yield from modify_optical_pipe_form_pages(pipe)))

    summary_fields = ["customer_id", "optical_pipe_name"]
    yield from modify_summary_form(
        user_input_dict,
        pipe,
        summary_fields,
        extra_before={"customer_id": subscription.customer_id},
    )

    return user_input_dict | {"subscription": subscription}


__all__ = [
    "OPTICAL_MODULE_BLOCK_STATE_KEY",
    "PIPE_NODE_ROLES",
    "PORT_BLOCK_CLASS_BY_ROLE",
    "check_pipe_terminations",
    "configure_pipe_terminations",
    "create_optical_pipe_form_generator",
    "create_pipe_form_pages",
    "default_pipe_identifier",
    "default_pipe_identifier_of",
    "get_pipe_ports",
    "load_optical_pipe_block",
    "modify_optical_pipe_form",
    "modify_optical_pipe_form_generator",
    "modify_optical_pipe_form_pages",
    "multiple_optical_pipe_selector",
    "new_optical_pipe_subscription",
    "new_pipe_port_block",
    "optical_pipe_block_from_state",
    "optical_pipe_selector",
    "optical_pipe_subscription_description",
    "pipe_nodes_form",
    "pipe_port_roles",
    "pipe_termination_label",
    "pipe_terminations_form",
    "resolve_port_role",
    "set_optical_pipe_subscription_description",
    "update_optical_pipe_block",
]
