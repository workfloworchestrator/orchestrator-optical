"""Create Optical Leased Spectrum workflow.

This module ships the ready-to-use ``create_leased_spectrum`` workflow for
the shipped Optical Leased Spectrum product type, together with the
importable parts: the FormPages of the create form (as the
:func:`create_leased_spectrum_form_pages` page sequence), the block
population logic and the step list that operates on the Optical Leased
Spectrum block found in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model, populates its block with the create-form values (the mandatory fields
of the PROVISIONING lifecycle) and transitions it to PROVISIONING, the shipped
block steps configure the leased spectrum terminations on the devices, refresh
the passbands in use and persist the PROVISIONING block found in the state
under ``OPTICAL_MODULE_BLOCK_STATE_KEY``, and the shipped description step
finalizes the subscription. The
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

from typing import cast
from uuid import UUID, uuid4

from pydantic import ConfigDict, Field
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.db import node_block_from_subscription
from orchestrator.optical.hal.optical_port import (
    get_device_client_ports_names,
    get_device_line_ports_names,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_port.unions import LeasedSpectrumPortBlockInactive
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumInactive,
    OpticalLeasedSpectrumProvisioning,
)
from orchestrator.optical.workflows.optical_pipe.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    configure_pipe_terminations,
    create_optical_pipe_form_generator,
    create_pipe_form_pages,
    leased_spectrum_port_block_class,
    new_optical_pipe_subscription,
    new_pipe_port_block,
    retrieve_optical_pipe_used_passbands,
    save_optical_pipe_block,
    set_optical_pipe_subscription_description,
)


def leased_spectrum_ports_of_node(node_block: AbstractOpticalNodeBlockInactive) -> list[str]:
    """Return the ports of a node that can terminate a leased spectrum pipe.

    On a Nokia FlexILS node only the OLS add/drop (SCG) ports are selectable: the
    OTS ports are OLS line ports that the FlexILS HAL cannot configure end-to-end
    for a leased spectrum pipe. On Groove G30 and GX G42 nodes only the line ports
    are selectable; the client ports are not part of the leased spectrum port block
    union.
    """
    if (
        node_block.management.optical_module_node_vendor,
        node_block.management.optical_module_node_platform,
    ) == (Vendor.NOKIA, Platform.FLEXILS):
        return get_device_client_ports_names(node_block)
    return list(dict.fromkeys(get_device_line_ports_names(node_block)))


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

    This is the shipped create form as a page sequence: it yields the two-nodes
    page and the terminations page, and returns the collected user input as a
    flat dict of the ``optical_*`` state keys, consumed by the shipped
    construct step (:func:`construct_leased_spectrum_subscription`). A Leased
    Spectrum pipe is terminated by the OLS add/drop (SCG) ports of a Nokia
    FlexILS node, or by the line ports of a Groove G30 or GX G42 node
    (:func:`leased_spectrum_ports_of_node`); the terminations page also collects
    the third-party provider name. Consumers yield from it in one line inside
    their own create form generator, optionally interleaving their own pages.
    The customer of the subscription is collected separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    return create_pipe_form_pages(
        product_name,
        port_universe=leased_spectrum_ports_of_node,
        port_prompt="Select an unused line or add/drop port on {fqdn}",
        distinct_nodes_message="The two ends of a leased spectrum pipe must be on different nodes.",
        terminations_form=create_leased_spectrum_terminations_form,
    )


def create_leased_spectrum_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Leased Spectrum pipe.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    construct step (:func:`construct_leased_spectrum_subscription`). It is a
    thin composition of the shipped page sequence
    (:func:`create_leased_spectrum_form_pages`) and the summary form.

    Args:
        product_name: Name of the product being created.
    """
    return (
        yield from create_optical_pipe_form_generator(
            product_name,
            create_leased_spectrum_form_pages,
            [
                "customer_id",
                "provider_name",
                "optical_pipe_name",
                "node_a_id",
                "port_a_name",
                "node_b_id",
                "port_b_name",
            ],
        )
    )


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
    call it from their own construct step to build the shipped block with its
    two terminating port blocks (created on their host nodes), before their
    subscription model is transitioned to the PROVISIONING lifecycle. The
    third-party provider name is prefixed to the pipe name (the
    leased-spectrum provider prefixing business logic lives here, in the
    anti-corruption point).

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
        The inactive Optical Leased Spectrum block with its two terminations.
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


@step("Construct Leased Spectrum Subscription")
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
    """Construct the PROVISIONING domain subscription model for an Optical Leased Spectrum pipe.

    This step builds the shipped ``OpticalLeasedSpectrum`` model, populates
    its block with the create-form values through
    :func:`build_leased_spectrum_block` (the anti-corruption point) and
    transitions the subscription to PROVISIONING in memory, so the block
    found in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` is the
    PROVISIONING variant with its terminations already set — the contract of
    the shipped block steps of
    :data:`CREATE_LEASED_SPECTRUM_BLOCK_STEPS`. The subscription description
    is not set here: it is finalized by the shipped description step.

    Consumers that define their own product type (composing the
    ``OpticalLeasedSpectrumBlock`` under their own attribute name) write their
    own construct step instead: it builds their subscription, populates the
    composed block with the mandatory fields set (e.g. via
    :func:`build_leased_spectrum_block`), transitions it to PROVISIONING and
    puts the block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
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
        OPTICAL_MODULE_BLOCK_STATE_KEY: subscription.optical_pipe,
    }


#: Create steps operating on the Optical Leased Spectrum block in the state.
#: Every step is block-level: the terminations are configured on the
#: devices, the passbands in use are refreshed and the block (with the
#: refreshed passbands) is persisted by the last step, because workflow steps
#: execute with the state serialized between steps (the block is re-hydrated
#: from its serialized form before every step operates on it). The block is
#: assumed to be in the PROVISIONING lifecycle status with its terminations
#: already set: the caller's construct step provides it (see
#: :func:`construct_leased_spectrum_subscription`). Consumers with their own
#: model run this list after constructing their subscription the same way and
#: putting their block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
CREATE_LEASED_SPECTRUM_BLOCK_STEPS: StepList = (
    begin >> configure_pipe_terminations >> retrieve_optical_pipe_used_passbands >> save_optical_pipe_block
)


@create_workflow(initial_input_form=create_leased_spectrum_form_generator)
def create_leased_spectrum() -> StepList:
    """Workflow to create a new Optical Leased Spectrum pipe.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalLeasedSpectrum` model, populates its block with
    the create-form values and transitions it to PROVISIONING, the shipped
    block steps configure the leased spectrum terminations on the devices,
    refresh the passbands in use and persist the block, and the shipped
    description step finalizes the subscription. It is therefore only valid
    for the shipped product type; consumers with their own product type
    compose their own create workflow with the same parts.
    """
    return (
        begin
        >> construct_leased_spectrum_subscription
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> CREATE_LEASED_SPECTRUM_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_LEASED_SPECTRUM_BLOCK_STEPS",
    "build_leased_spectrum_block",
    "create_leased_spectrum",
    "create_leased_spectrum_form_pages",
]
