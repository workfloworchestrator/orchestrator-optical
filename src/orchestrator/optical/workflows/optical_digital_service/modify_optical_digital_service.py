"""Modify Optical Digital Service workflow.

This module ships the ready-to-use ``modify_optical_digital_service`` workflow
for the shipped Optical Digital Service product type, together with the
importable parts: the FormPage of the modify form (as the
:func:`modify_optical_digital_service_form_pages` page sequence, prefilled with
the current block values) and the step list that updates and persists
the Optical Digital Service block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Only the service and transport channel names, the central frequencies,
spectral widths, operating mode and the OLS interior path can be modified:
the endpoints, client/line ports and number of carriers are fixed. Path
changes and channel renames apply to service-owned channels only; reused
channels keep the sections and names of their owning subscription.
Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages. The consumer extracts the
block with plain Python at any nesting depth (shipped code never traverses
the subscription)::

    block = subscription.optical_module_block  # or subscription.router.optical_module
    user_input_dict = yield from modify_optical_digital_service_form_pages(block, product_name=...)
    user_input_dict.update((yield my_own_page).model_dump())
"""

from time import sleep
from typing import Any

from pydantic import model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.hal.adapters.nokia_flexils.spectrum import FLEXILS_SPECTRAL_GRID_MHZ
from orchestrator.optical.products.product_blocks.optical_digital_service import (
    OpticalDigitalServiceBlock,
    OpticalDigitalServiceBlockInactive,
)
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSubscription
from orchestrator.optical.utils.custom_types.frequencies import (
    Frequency,
    SpectralWidth,
    ensure_passband_aligned_to_grid,
    passband_from,
)
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service import (
    create_optical_digital_service_path_form,
    decode_optical_path,
    no_optical_path_placeholder_choice,
    optical_digital_service_path_choice,
)
from orchestrator.optical.workflows.optical_digital_service.shared import (
    align_optical_digital_tx_power,
    channel_names_taken_by_others,
    configure_optical_digital_client_ports,
    configure_optical_digital_crossconnects,
    configure_optical_digital_line_ports,
    ensure_circuit_label_token_valid,
    get_transceiver_capacity_from_mode,
    has_flexils_sections,
    is_new_channel,
    load_optical_digital_service_block,
    modify_optical_digital_sections,
    optical_digital_service_block_from_state,
    optical_transport_mode_selector,
    refresh_optical_digital_used_passbands,
    reject_placeholder_transport_mode,
    set_optical_digital_service_subscription_description,
    update_optical_digital_sections_path,
    validate_line_port_mode,
    validated_channel_names,
)
from orchestrator.optical.workflows.optical_pipe.shared import multiple_optical_pipe_selector
from orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum_service import (
    create_optical_spectrum_constraints_form,
    create_optical_spectrum_waypoints_form,
)
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    LINE_SYSTEM_ROLES,
    NoOpticalPathFoundError,
    multiple_optical_node_selector,
)
from orchestrator.optical.workflows.shared import modify_summary_form

logger = get_logger(__name__)

#: Seconds to wait for the retuned lasers and ROADMs to settle before measuring power.
SETTLE_AFTER_RETUNE_S = 10


def modify_optical_digital_service_identity_form(block: OpticalDigitalServiceBlock) -> type[FormPage]:
    """Return the identity FormPage of the Optical Digital Service modify form.

    The page is prefilled with the current service name and transport channel
    names, so unchanged fields remain intact. Only service-owned channels can
    be renamed: a reused channel belongs to another subscription, and a name
    colliding with another service's channel is rejected (it would hijack the
    channel reuse identity). Renaming a service or channel whose circuits are
    shared leaves the composite labels of borrower services stale until their
    next ensure/reconcile (cosmetic only: the device-side circuit identity
    never changes). The ownership and collision checks run here as an
    early hint and authoritatively in
    :func:`update_optical_digital_service_block`.

    Args:
        block: The Optical Digital Service block being modified.

    Returns:
        The prefilled identity FormPage of the shipped modify form.
    """
    channels = block.optical_digital_service_transport_channels

    def _check_names(service_name: str, first: str, second: str | None = None) -> None:
        ensure_circuit_label_token_valid(service_name, "digital service")
        current_names = [str(channel.optical_transport_channel_name) for channel in channels]
        owned_flags = [str(channel.owner_subscription_id) == str(block.owner_subscription_id) for channel in channels]
        taken = channel_names_taken_by_others({str(channel.subscription_instance_id) for channel in channels})
        validated_channel_names(current_names, owned_flags, first, second, taken)

    class ModifyOpticalDigitalServiceIdentityForm(FormPage):
        optical_digital_service_name: str = block.optical_digital_service_name
        channel_name_1: str = str(channels[0].optical_transport_channel_name)

        @model_validator(mode="after")
        def validate_names(self) -> "ModifyOpticalDigitalServiceIdentityForm":
            _check_names(self.optical_digital_service_name, self.channel_name_1)
            return self

    if len(channels) == 1:
        return ModifyOpticalDigitalServiceIdentityForm

    class ModifyOpticalDigitalServiceDualIdentityForm(ModifyOpticalDigitalServiceIdentityForm):
        channel_name_2: str = str(channels[1].optical_transport_channel_name)

        @model_validator(mode="after")
        def validate_second_name(self) -> "ModifyOpticalDigitalServiceDualIdentityForm":
            _check_names(self.optical_digital_service_name, self.channel_name_1, self.channel_name_2)
            return self

    return ModifyOpticalDigitalServiceDualIdentityForm


def modify_optical_digital_service_form(block: OpticalDigitalServiceBlock) -> type[FormPage]:
    """Return the modify FormPage of the Optical Digital Service subscription.

    The page is prefilled with the current frequencies, bandwidths and mode of
    the transport channels, so unchanged fields remain intact. The mode is a
    drop-down over the intersection of the live mode tables of the channels'
    line port cards (see :func:`optical_transport_mode_selector
    <orchestrator.optical.workflows.optical_digital_service.shared.optical_transport_mode_selector>`);
    the currently provisioned mode is always offered, so the prefilled page
    renders even when the stored mode went stale. The number of
    fields follows the number of channels: services with two channels
    (reverse multiplexing) expose the second frequency/bandwidth pair.

    Args:
        block: The Optical Digital Service block being modified.

    Returns:
        The prefilled modify FormPage of the shipped modify form.
    """
    channels = block.optical_digital_service_transport_channels
    old_mode = channels[0].optical_transport_mode
    line_port_ids = [
        str(line_port.subscription_instance_id)
        for channel in channels
        for line_port in channel.optical_transport_line_ports
    ]
    mode_choice = optical_transport_mode_selector(line_port_ids, extra_options=[str(old_mode)])

    class ModifyOpticalDigitalServiceForm(FormPage):
        optical_transport_mode: mode_choice = old_mode
        frequency_1: Frequency = channels[0].optical_transport_central_frequency
        bandwidth_1: SpectralWidth = (
            channels[0].optical_transport_spectrum.optical_spectrum_passband[1]
            - channels[0].optical_transport_spectrum.optical_spectrum_passband[0]
        )

        @model_validator(mode="after")
        def validate_data(self) -> "ModifyOpticalDigitalServiceForm":
            reject_placeholder_transport_mode(str(self.optical_transport_mode))
            ensure_passband_aligned_to_grid(
                passband_from(self.frequency_1, self.bandwidth_1), FLEXILS_SPECTRAL_GRID_MHZ
            )
            return self

    if len(channels) == 1:
        return ModifyOpticalDigitalServiceForm

    class ModifyOpticalDigitalServiceDualForm(ModifyOpticalDigitalServiceForm):
        frequency_2: Frequency = channels[1].optical_transport_central_frequency
        bandwidth_2: SpectralWidth = (
            channels[1].optical_transport_spectrum.optical_spectrum_passband[1]
            - channels[1].optical_transport_spectrum.optical_spectrum_passband[0]
        )

        @model_validator(mode="after")
        def validate_second_channel(self) -> "ModifyOpticalDigitalServiceDualForm":
            ensure_passband_aligned_to_grid(
                passband_from(self.frequency_2, self.bandwidth_2), FLEXILS_SPECTRAL_GRID_MHZ
            )
            return self

    return ModifyOpticalDigitalServiceDualForm


def _yield_modify_routing_constraint_pages(product_name: str) -> FormGenerator:
    """Yield the waypoints and constraints pages of the Optical Digital Service modify form.

    Returns the collected input (``intermediate_node_instance_ids``,
    ``exclude_node_instance_ids``, ``exclude_pipe_instance_ids``); the caller merges it.

    Args:
        product_name: Name of the product being modified, used as the page title.

    Returns:
        The collected user input of the routing pages.
    """
    waypoints_choice = multiple_optical_node_selector(
        roles=LINE_SYSTEM_ROLES,
        prompt="Which Optical Nodes must the path pass through?",
    )
    collected = (yield create_optical_spectrum_waypoints_form(product_name, waypoints_choice)).model_dump()

    exclude_nodes_choice = multiple_optical_node_selector(
        roles=LINE_SYSTEM_ROLES,
        prompt="Do *not* pass through these Optical Nodes",
    )
    exclude_spans_choice = multiple_optical_pipe_selector(
        prompt="Do *not* pass through these Optical Pipes",
    )
    collected.update(
        (
            yield create_optical_spectrum_constraints_form(product_name, exclude_nodes_choice, exclude_spans_choice)
        ).model_dump()
    )
    return collected


def modify_optical_digital_service_form_pages(
    block: OpticalDigitalServiceBlock,
    *,
    product_name: str,
) -> FormGenerator:
    """Yield the FormPages of the Optical Digital Service modify form, in order.

    This is the shipped modify form as a page sequence: it yields the prefilled
    identity page (service and transport channel names), the prefilled channels
    page (mode, frequencies) and, only when the first transport channel is
    service-owned with deployed OLS sections, the waypoints page, the
    constraints page and the path page. The optical path is recomputed between
    the fixed line ports of the first channel (endpoints and ports never
    change) with the new passband of the channels page, mirroring the shipped
    create form; the second channel of a reverse-multiplexed pair derives its
    path from the chosen one in :func:`update_optical_digital_sections_path
    <orchestrator.optical.workflows.optical_digital_service.shared.update_optical_digital_sections_path>`.
    It returns the collected user input as a flat dict of the ``optical_*``
    state keys, consumed by the shipped steps of
    :data:`MODIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS`. Consumers yield from it
    in one line inside their own modify form generator, optionally interleaving
    their own pages. The customer of the subscription is collected separately
    by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        block: The Optical Digital Service block being modified.
        product_name: Name of the product being modified, used as the page title
            of the reused routing pages.

    Returns:
        The collected user input of the shipped pages.
    """
    channels = block.optical_digital_service_transport_channels
    user_input_dict: dict[str, Any] = {}
    user_input_dict.update((yield modify_optical_digital_service_identity_form(block)).model_dump())
    user_input_dict.update((yield modify_optical_digital_service_form(block)).model_dump())

    reference = channels[0]
    if (
        str(reference.owner_subscription_id) != str(block.owner_subscription_id)
        or not reference.optical_transport_spectrum.optical_spectrum_sections
    ):
        return user_input_dict

    user_input_dict.update((yield from _yield_modify_routing_constraint_pages(product_name)))

    line_ports = reference.optical_transport_line_ports
    passband = passband_from(user_input_dict["frequency_1"], user_input_dict["bandwidth_1"])
    try:
        path_choice = optical_digital_service_path_choice(
            str(line_ports[0].subscription_instance_id),
            str(line_ports[1].subscription_instance_id),
            user_input_dict["intermediate_node_instance_ids"],
            passband,
            user_input_dict["exclude_node_instance_ids"],
            user_input_dict["exclude_pipe_instance_ids"],
        )
    except (NoOpticalPathFoundError, ValueError):
        # No path (or an unresolvable fiber attachment): the form offers the
        # rejecting placeholder so the user adjusts the constraints.
        logger.exception(
            "No optical path found",
            passband=passband,
        )
        path_choice = no_optical_path_placeholder_choice()

    user_input_dict.update((yield create_optical_digital_service_path_form(path_choice)).model_dump())
    user_input_dict["optical_path"] = decode_optical_path(user_input_dict["optical_path"])
    return user_input_dict


def modify_optical_digital_service_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalDigitalServiceSubscription,
    block_field_name: str = "optical_digital_service",
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Digital Service.

    The form is prefilled with the current values of the block, so
    unchanged fields remain intact. It is a thin composition of the customer
    page, the shipped page sequence
    (:func:`modify_optical_digital_service_form_pages`) and the summary form.
    Shipped-product only: consumers compose their own form generator from the
    shipped page sequence.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical
            Digital Service product.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Digital Service block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    block = getattr(subscription, block_field_name)

    user_input_dict = yield from customer_choice_form_page(include=str(subscription.customer_id))
    user_input_dict.update(
        (yield from modify_optical_digital_service_form_pages(block, product_name=subscription.product.name))
    )

    summary_fields = [
        "customer_id",
        "optical_digital_service_name",
        "channel_name_1",
        "optical_transport_mode",
        "frequency_1",
        "bandwidth_1",
    ]
    if len(block.optical_digital_service_transport_channels) == 2:  # noqa: PLR2004
        summary_fields.extend(["channel_name_2", "frequency_2", "bandwidth_2"])
    yield from modify_summary_form(
        user_input_dict,
        block,
        summary_fields,
        extra_before={"customer_id": str(subscription.customer_id)},
    )

    return user_input_dict | {"subscription": subscription}


@step("Updating Optical Digital Service block")
def update_optical_digital_service_block(
    optical_module_block: OpticalDigitalServiceBlockInactive,
    optical_transport_mode: str,
    frequency_1: Frequency,
    bandwidth_1: SpectralWidth,
    frequency_2: Frequency | None = None,
    bandwidth_2: SpectralWidth | None = None,
    optical_digital_service_name: str | None = None,
    channel_name_1: str | None = None,
    channel_name_2: str | None = None,
) -> State:
    """Update the transport channels of the block in the state from the modify-form keys.

    Every channel keeps its ports and sections: only the service name, the
    channel names, the central frequency, the passband (recomputed as
    ``frequency ± bandwidth / 2``) and the mode are overwritten. The name
    parameters default to ``None`` (keep the current value) so callers that
    predate the rename support keep working. A channel rename also renames its
    spectrum (``"<channel> spectrum"``, as the create workflow names it); the
    device-side circuit identity (the spectrum subscription instance id) never
    changes, so the circuits are converged by identity by the following steps
    (borrower services sharing the renamed circuits keep their stale composite
    labels until their next ensure/reconcile).
    The previous section subscription instance ids and passbands are snapshotted
    per channel into the state, so the following section steps can detect a
    path change. The new mode is validated against the live mode tables of the
    channels' line port cards before anything is mutated (see :func:`validate_line_port_mode
    <orchestrator.optical.workflows.optical_digital_service.shared.validate_line_port_mode>`).
    The total capacity is re-derived from the new mode on the
    service-owned channels only: reused channels keep the capacity accounting
    of their owning subscription. The circuits are converged by identity by the
    following steps, so the old passbands are not needed anymore.
    Workflow steps execute with the state serialized between steps, so the block
    is re-hydrated from its serialized form before it is updated.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY`` (the provisioning variant, while
            the subscription is being modified).
        optical_transport_mode: The new operating mode of all transport channels.
        frequency_1: The new central frequency of the first channel in MHz.
        bandwidth_1: The new spectral width of the first channel in MHz.
        frequency_2: The new central frequency of the second channel in MHz, if any.
        bandwidth_2: The new spectral width of the second channel in MHz, if any.
        optical_digital_service_name: The new user-facing service name, or
            ``None`` to keep the current one.
        channel_name_1: The new name of the first transport channel, or ``None``
            to keep the current one.
        channel_name_2: The new name of the second transport channel, or
            ``None`` to keep the current one.

    Raises:
        ValueError: If the form channel count does not match the block channel count.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    channels = list(block.optical_digital_service_transport_channels)
    new_values: list[tuple[Frequency, SpectralWidth]] = [(frequency_1, bandwidth_1)]
    if frequency_2 is not None and bandwidth_2 is not None:
        new_values.append((frequency_2, bandwidth_2))
    if len(new_values) != len(channels):
        msg = "The number of carriers cannot be changed by the modify workflow"
        raise ValueError(msg)
    old_channel_sections = {
        str(channel.subscription_instance_id): [
            str(section.subscription_instance_id)
            for section in channel.optical_transport_spectrum.optical_spectrum_sections
        ]
        for channel in channels
    }
    old_channel_passbands = {
        str(channel.subscription_instance_id): list(channel.optical_transport_spectrum.optical_spectrum_passband)
        for channel in channels
    }
    if optical_digital_service_name is not None:
        block.optical_digital_service_name = ensure_circuit_label_token_valid(
            optical_digital_service_name, "digital service"
        )
    current_names = [str(channel.optical_transport_channel_name) for channel in channels]
    if channel_name_1 is None and channel_name_2 is None:
        new_names = current_names
    else:
        owned_flags = [is_new_channel(channel, block) for channel in channels]
        taken_names = channel_names_taken_by_others({str(channel.subscription_instance_id) for channel in channels})
        new_names = validated_channel_names(current_names, owned_flags, channel_name_1, channel_name_2, taken_names)
    for channel in channels:
        channel_name = str(channel.optical_transport_channel_name)
        for line_port in channel.optical_transport_line_ports:
            validate_line_port_mode(
                str(line_port.subscription_instance_id), optical_transport_mode, f"channel {channel_name}"
            )
    for channel, (frequency, bandwidth), new_name in zip(channels, new_values, new_names, strict=True):
        channel.optical_transport_central_frequency = frequency
        channel.optical_transport_spectrum.optical_spectrum_passband = passband_from(frequency, bandwidth)
        channel.optical_transport_mode = optical_transport_mode
        if new_name != str(channel.optical_transport_channel_name):
            channel.optical_transport_channel_name = new_name
            channel.optical_transport_spectrum.optical_spectrum_name = f"{new_name} spectrum"
        if is_new_channel(channel, block):
            hosts = [line.optical_port_host_node for line in channel.optical_transport_line_ports]
            channel.optical_transport_total_capacity = get_transceiver_capacity_from_mode(hosts, optical_transport_mode)
    return {
        OPTICAL_MODULE_BLOCK_STATE_KEY: block,
        "old_channel_sections": old_channel_sections,
        "old_channel_passbands": old_channel_passbands,
    }


@step("Waiting for the retune to settle")
def wait_for_retune_to_settle(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Wait for the retuned lasers and ROADMs to settle before measuring power.

    The step sleeps only when the block holds channels with FlexILS sections;
    pure transponder services skip the wait.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    if has_flexils_sections(block):
        sleep(SETTLE_AFTER_RETUNE_S)
    return {}


#: Modify steps operating on the Optical Digital Service block in the state. The block
#: is persisted by the last step, because workflow steps reload the subscription
#: from the database and would otherwise lose the mutations.
MODIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS: StepList = (
    begin
    >> update_optical_digital_service_block
    >> update_optical_digital_sections_path
    >> configure_optical_digital_line_ports
    >> configure_optical_digital_client_ports
    >> configure_optical_digital_crossconnects
    >> modify_optical_digital_sections
    >> refresh_optical_digital_used_passbands
    >> wait_for_retune_to_settle
    >> align_optical_digital_tx_power
    >> save_optical_module_block
)


@modify_workflow(initial_input_form=modify_optical_digital_service_form_generator)
def modify_optical_digital_service() -> StepList:
    """Workflow to modify an existing Optical Digital Service subscription.

    The workflow is valid for the shipped :class:`OpticalDigitalService` product
    type only: it loads the block from the ``optical_digital_service`` attribute
    of the shipped subscription models. The service and transport channel names,
    frequencies, bandwidths, mode and the OLS interior path are modified;
    endpoints, ports and carrier count are fixed. Path changes and channel
    renames apply to service-owned channels only.
    Consumers with their own product type compose their own modify workflow
    with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_digital_service_block
        >> MODIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS
        >> set_optical_digital_service_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS",
    "SETTLE_AFTER_RETUNE_S",
    "modify_optical_digital_service",
    "modify_optical_digital_service_form",
    "modify_optical_digital_service_form_generator",
    "modify_optical_digital_service_form_pages",
    "modify_optical_digital_service_identity_form",
    "update_optical_digital_service_block",
    "wait_for_retune_to_settle",
]
