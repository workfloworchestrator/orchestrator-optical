"""Create Optical Leased Spectrum workflow.

This module ships the ready-to-use ``create_leased_spectrum`` workflow for
the shipped Optical Leased Spectrum product type, together with the
importable parts: the FormPages of the create form (as the
:func:`create_leased_spectrum_form_pages` page sequence), the block
population logic and the step list that operates on the Optical Leased
Spectrum block found in the state under ``OPTICAL_PIPE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model and puts its block in the state, the shipped block steps persist the
block, and the shipped description step finalizes the subscription. The
shipped form generator is a thin composition of the shipped pages and the
summary form, without hooks: consumers build their own form generator by
yielding from the shipped page sequence in one line and adding their own
pages::

    user_input_dict = yield from create_leased_spectrum_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

The subscription model has no dedicated provider field: the ``provider_name``
collected by the form is always persisted by prefixing it to the
``optical_pipe_name`` (``"<provider> <circuit id or default>"``), so that no
input is silently dropped.
"""

from typing import Any, cast
from uuid import UUID, uuid4

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.db import node_block_from_subscription
from orchestrator.optical.hal.optical_node import Vendor, retrieve_ports_spectral_occupations, vendor_of
from orchestrator.optical.hal.optical_port import (
    configure_termination_when_attaching_new_fiber,
    get_device_client_ports_names,
    get_device_line_ports_names,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_port.unions import LeasedSpectrumPortBlockInactive
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumInactive,
    OpticalLeasedSpectrumProvisioning,
)
from orchestrator.optical.workflows.customer import customer_choice_form_pages
from orchestrator.optical.workflows.optical_pipe.shared import (
    OPTICAL_PIPE_BLOCK_STATE_KEY,
    default_pipe_identifier,
    leased_spectrum_port_block_class,
    new_optical_pipe_subscription,
    new_pipe_port_block,
    optical_node_selector,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
    unused_node_port_selector,
)
from orchestrator.optical.workflows.shared import create_summary_form


def leased_spectrum_ports_of_node(node_block: AbstractOpticalNodeBlockInactive) -> list[str]:
    """Return the ports of a node that can terminate a leased spectrum pipe.

    On a Nokia FlexILS node only the OLS add/drop (SCG) ports are selectable: the
    OTS ports are OLS line ports that the FlexILS HAL cannot configure end-to-end
    for a leased spectrum pipe. On Groove G30 and GX G42 nodes only the line ports
    are selectable; the client ports are not part of the leased spectrum port block
    union.
    """
    if vendor_of(node_block) == Vendor.FLEXILS:
        return get_device_client_ports_names(node_block)
    return list(dict.fromkeys(get_device_line_ports_names(node_block)))


def create_leased_spectrum_identity_form(
    product_name: str,
    node_choice: type[Choice],
) -> type[FormPage]:
    """Return the identity FormPage of the Optical Leased Spectrum create form.

    This is the first page of the shipped create form: the two optical nodes the
    leased spectrum pipe connects. It is a building block for consumers that
    compose their own create form generator: the shipped page sequence
    (:func:`create_leased_spectrum_form_pages`) yields it first. The page
    validates that the two ends of the pipe are on different nodes.

    Args:
        product_name: Name of the product being created, used as the page title.
        node_choice: The ``Choice`` selector of the optical node subscriptions,
            as built by :func:`orchestrator.optical.workflows.optical_pipe.shared.optical_node_selector`.

    Returns:
        The identity FormPage of the shipped create form.
    """

    class CreateLeasedSpectrumIdentityForm(FormPage):
        model_config = ConfigDict(title=product_name)

        node_a_id: node_choice
        node_b_id: node_choice

        @model_validator(mode="after")
        def validate_distinct_nodes(self) -> "CreateLeasedSpectrumIdentityForm":
            """Raise if the two ends of the pipe are on the same node."""
            if self.node_a_id == self.node_b_id:
                msg = "The two ends of a leased spectrum pipe must be on different nodes."
                raise ValueError(msg)
            return self

    return CreateLeasedSpectrumIdentityForm


def create_leased_spectrum_terminations_form(
    product_name: str,
    port_a_choice: type[Choice],
    port_b_choice: type[Choice],
) -> type[FormPage]:
    """Return the terminations FormPage of the Optical Leased Spectrum create form.

    This is the second page of the shipped create form: the third-party provider
    name, the optional leased spectrum identifier and the two terminating ports.
    It is a building block for consumers that compose their own create form
    generator: the shipped page sequence
    (:func:`create_leased_spectrum_form_pages`) yields it second.

    Args:
        product_name: Name of the product being created, used as the page title.
        port_a_choice: The ``Choice`` selector of the unused ports of the first node.
        port_b_choice: The ``Choice`` selector of the unused ports of the second node.

    Returns:
        The terminations FormPage of the shipped create form.
    """

    class CreateLeasedSpectrumTerminationsForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Terminations")

        provider_name: str = Field(..., title="Third-Party Provider Name", min_length=1)
        optical_pipe_name: str | None = Field(
            None,
            title="Leased Spectrum Identifier",
            description="Circuit ID or provider reference. Leave empty to use the default "
            "'<node A> <port A> --- <node B> <port B>'. The provider name is always prefixed.",
        )
        port_a_name: port_a_choice
        port_b_name: port_b_choice

    return CreateLeasedSpectrumTerminationsForm


def create_leased_spectrum_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Optical Leased Spectrum create form, in order.

    This is the shipped create form as a page sequence: it yields the identity
    page and the terminations page, and returns the collected user input as a
    flat dict of the ``optical_*`` state keys, consumed by the shipped steps of
    :data:`CREATE_LEASED_SPECTRUM_BLOCK_STEPS`. Consumers yield from it in one
    line inside their own create form generator, optionally interleaving their
    own pages. The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_pages`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    node_choice = optical_node_selector(prompt="This leased spectrum connects this node:")

    user_input_dict: dict[str, Any] = {}
    user_input_dict.update((yield create_leased_spectrum_identity_form(product_name, node_choice)).model_dump())

    node_a_block = node_block_from_subscription(user_input_dict["node_a_id"])
    node_b_block = node_block_from_subscription(user_input_dict["node_b_id"])

    port_a_choice = unused_node_port_selector(
        user_input_dict["node_a_id"],
        leased_spectrum_ports_of_node(node_a_block),
        prompt=f"Select an unused line or add/drop port on {node_a_block.management.optical_module_node_fqdn}",
    )
    port_b_choice = unused_node_port_selector(
        user_input_dict["node_b_id"],
        leased_spectrum_ports_of_node(node_b_block),
        prompt=f"Select an unused line or add/drop port on {node_b_block.management.optical_module_node_fqdn}",
    )

    user_input_dict.update(
        (yield create_leased_spectrum_terminations_form(product_name, port_a_choice, port_b_choice)).model_dump()
    )

    user_input_dict["optical_pipe_name"] = user_input_dict["optical_pipe_name"] or default_pipe_identifier(
        node_a_block, user_input_dict["port_a_name"], node_b_block, user_input_dict["port_b_name"]
    )

    return user_input_dict


def create_leased_spectrum_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Leased Spectrum pipe.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_LEASED_SPECTRUM_BLOCK_STEPS`. It is a thin
    composition of the shipped page sequence
    (:func:`create_leased_spectrum_form_pages`) and the summary form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from customer_choice_form_pages(title=product_name)
    user_input_dict.update((yield from create_leased_spectrum_form_pages(product_name)))

    summary_fields = [
        "customer_id",
        "provider_name",
        "optical_pipe_name",
        "node_a_id",
        "port_a_name",
        "node_b_id",
        "port_b_name",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


def build_leased_spectrum_block(
    subscription_id: UUID,
    node_a_id: UUIDstr,
    node_b_id: UUIDstr,
    port_a_name: str,
    port_b_name: str,
    provider_name: str,
    optical_pipe_name: str,
) -> OpticalLeasedSpectrumBlockInactive:
    """Build the Optical Leased Spectrum block of a subscription from the create-form keys.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step on the shipped block they compose,
    before their subscription model is transitioned to the next lifecycle. The
    two terminating port blocks are created on their host nodes, and the
    third-party provider name is prefixed to the pipe name (the leased-spectrum
    provider prefixing business logic lives here, in the anti-corruption point).

    Args:
        subscription_id: Subscription id of the pipe subscription owning the block.
        node_a_id: Subscription id of the optical node hosting the first termination.
        node_b_id: Subscription id of the optical node hosting the second termination.
        port_a_name: Name of the first terminating port on its device.
        port_b_name: Name of the second terminating port on its device.
        provider_name: Name of the third-party provider; it is stripped and prefixed
            to the pipe name.
        optical_pipe_name: Name (circuit id or provider reference) of the pipe.

    Returns:
        The built Optical Leased Spectrum block in the INITIAL state.
    """
    node_a_block = node_block_from_subscription(node_a_id)
    node_b_block = node_block_from_subscription(node_b_id)

    client_ports_a = get_device_client_ports_names(node_a_block)
    client_ports_b = get_device_client_ports_names(node_b_block)
    port_a = new_pipe_port_block(
        subscription_id,
        node_a_block,
        port_a_name,
        f"Physically connected to {node_b_block.management.optical_module_node_fqdn} {port_b_name}.",
        leased_spectrum_port_block_class(node_a_block, port_a_name, client_ports_a),
    )
    port_b = new_pipe_port_block(
        subscription_id,
        node_b_block,
        port_b_name,
        f"Physically connected to {node_a_block.management.optical_module_node_fqdn} {port_a_name}.",
        leased_spectrum_port_block_class(node_b_block, port_b_name, client_ports_b),
    )

    pipe_block = OpticalLeasedSpectrumBlockInactive.new(
        subscription_id=subscription_id,
        optical_pipe_terminations=cast(list[LeasedSpectrumPortBlockInactive], [port_a, port_b]),
    )
    provider_name = provider_name.strip()
    if provider_name:
        optical_pipe_name = f"{provider_name} {optical_pipe_name}"
    pipe_block.optical_pipe_name = optical_pipe_name

    return pipe_block


@step("Construct Leased Spectrum Model")
def construct_leased_spectrum_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    provider_name: str,
    node_a_id: UUIDstr,
    node_b_id: UUIDstr,
    port_a_name: str,
    port_b_name: str,
    optical_pipe_name: str,
) -> State:
    """Construct the initial domain subscription model for an Optical Leased Spectrum pipe.

    This step builds the shipped ``OpticalLeasedSpectrum`` model around a block
    assembled by :func:`build_leased_spectrum_block` and puts the block in the
    state under ``OPTICAL_PIPE_BLOCK_STATE_KEY`` for the shipped block steps of
    :data:`CREATE_LEASED_SPECTRUM_BLOCK_STEPS`. Consumers that define their own
    product type (composing the ``OpticalLeasedSpectrumBlock`` under their own
    attribute name) write their own construct step instead and can reuse
    :func:`build_leased_spectrum_block` as the anti-corruption point between
    their model and the shipped block. The subscription description is not set
    here: it is finalized by the shipped description step.
    """
    subscription_id = uuid4()
    pipe_block = build_leased_spectrum_block(
        subscription_id,
        node_a_id,
        node_b_id,
        port_a_name,
        port_b_name,
        provider_name,
        optical_pipe_name,
    )

    subscription = new_optical_pipe_subscription(OpticalLeasedSpectrumInactive, product, customer_id, pipe_block)
    subscription = OpticalLeasedSpectrumProvisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_PIPE_BLOCK_STATE_KEY: subscription.optical_pipe,
    }


@step("Configure Leased Spectrum Terminations")
def configure_leased_spectrum_terminations(subscription: OpticalLeasedSpectrumProvisioning) -> State:
    """Configure the terminating ports of the leased spectrum pipe on the devices."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    host_node_a = port_a.optical_port_host_node
    host_node_b = port_b.optical_port_host_node
    if not isinstance(host_node_a, AbstractOpticalNodeBlockInactive) or not isinstance(
        host_node_b, AbstractOpticalNodeBlockInactive
    ):
        msg = "Leased spectrum terminations must be hosted on Optical Nodes"
        raise TypeError(msg)
    if vendor_of(host_node_b) == Vendor.FLEXILS and vendor_of(host_node_a) != Vendor.FLEXILS:
        # Configure the FlexILS side first: its configuration references the remote node.
        port_a, port_b = port_b, port_a

    configuration_results = {
        f"{port_a.optical_port_host_node.management.optical_module_node_fqdn} {port_a.optical_port_name}": (
            configure_termination_when_attaching_new_fiber(port_a, port_b)
        ),
        f"{port_b.optical_port_host_node.management.optical_module_node_fqdn} {port_b.optical_port_name}": (
            configure_termination_when_attaching_new_fiber(port_b, port_a)
        ),
    }
    return {"configuration_results": configuration_results, "subscription": subscription}


@step("Retrieve Used Passbands")
def retrieve_leased_spectrum_used_passbands(subscription: OpticalLeasedSpectrumProvisioning) -> State:
    """Refresh the passbands in use on the terminating ports from the devices."""
    for port in subscription.optical_pipe.optical_pipe_terminations:
        if not isinstance(port, OlsAddDropPortBlockProvisioning | OlsLinePortBlockProvisioning):
            continue
        host_node = port.optical_port_host_node
        if host_node.optical_node_role not in (
            OpticalNodeRole.ROADM,
            OpticalNodeRole.TRANSPONDER_XOADM,
            OpticalNodeRole.AMPLIFIER,
        ):
            continue
        if port.optical_port_name is None:
            msg = f"Optical port block of {host_node.management.optical_module_node_fqdn} has no port name"
            raise ValueError(msg)
        port.optical_passbands = retrieve_ports_spectral_occupations(host_node).get(port.optical_port_name, [])
    return {"subscription": subscription}


#: Create steps operating on the Optical Leased Spectrum block in the state.
#: The block is re-hydrated from the database and persisted by the step,
#: because workflow steps execute with the state serialized between steps.
#: Consumers with their own model run this list after constructing their
#: (inactive) subscription and putting their block in the state under
#: ``OPTICAL_PIPE_BLOCK_STATE_KEY``.
CREATE_LEASED_SPECTRUM_BLOCK_STEPS: StepList = begin >> save_optical_pipe_block


@create_workflow(initial_input_form=create_leased_spectrum_form_generator)
def create_leased_spectrum() -> StepList:
    """Workflow to create a new Optical Leased Spectrum pipe.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalLeasedSpectrum` model and puts its block in the
    state, the shipped block steps persist the block, and the shipped
    description step finalizes the subscription before the terminations are
    configured on the devices. It is therefore only valid for the shipped
    product type; consumers with their own product type compose their own create
    workflow with the same parts.
    """
    return (
        begin
        >> construct_leased_spectrum_subscription
        >> CREATE_LEASED_SPECTRUM_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
        >> store_process_subscription()
        >> configure_leased_spectrum_terminations
        >> retrieve_leased_spectrum_used_passbands
    )


__all__ = [
    "CREATE_LEASED_SPECTRUM_BLOCK_STEPS",
    "create_leased_spectrum",
    "create_leased_spectrum_form_pages",
]
