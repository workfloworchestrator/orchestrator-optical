"""Modify Optical Digital Service workflow.

This module ships the ready-to-use ``modify_optical_digital_service`` workflow
for the shipped Optical Digital Service product type, together with the
importable parts: the FormPage of the modify form (as the
:func:`modify_optical_digital_service_form_pages` page sequence, prefilled with
the current subscription values) and the step list that updates and persists
the Optical Digital Service block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Only the central frequencies, spectral widths and operating mode can be
modified: the endpoints, ports, paths and number of carriers are fixed.
Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages::

    user_input_dict = yield from modify_optical_digital_service_form_pages(
        subscription, block_field_name="optical_digital_service"
    )
    user_input_dict.update((yield my_own_page).model_dump())
"""

from time import sleep

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_blocks.optical_digital_service import (
    OpticalDigitalServiceBlockInactive,
)
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalService
from orchestrator.optical.utils.custom_types.frequencies import Bandwidth, Frequency, Passband
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_digital_service.shared import (
    align_optical_digital_tx_power,
    configure_optical_digital_client_ports,
    configure_optical_digital_crossconnects,
    configure_optical_digital_line_ports,
    get_transceiver_capacity_from_mode,
    has_flexils_sections,
    is_new_channel,
    load_optical_digital_service_block,
    modify_optical_digital_sections,
    optical_digital_service_block_from_state,
    refresh_optical_digital_used_passbands,
    set_optical_digital_service_subscription_description,
)
from orchestrator.optical.workflows.shared import modify_summary_form


def modify_optical_digital_service_form(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_digital_service",
) -> type[FormPage]:
    """Return the modify FormPage of the Optical Digital Service subscription.

    The page is prefilled with the current frequencies, bandwidths and mode of
    the transport channels, so unchanged fields remain intact. The number of
    fields follows the number of channels: services with two channels
    (reverse multiplexing) expose the second frequency/bandwidth pair.

    Args:
        subscription: The ACTIVE subscription model of the Optical Digital
            Service product being modified (any consumer model that has-a the
            shipped block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Digital Service block.

    Returns:
        The prefilled modify FormPage of the shipped modify form.
    """
    block = getattr(subscription, block_field_name)
    channels = block.optical_digital_service_transport_channels
    old_mode = channels[0].optical_transport_mode

    class ModifyOpticalDigitalServiceForm(FormPage):
        optical_transport_mode: str = old_mode
        frequency_1: Frequency = channels[0].optical_transport_central_frequency
        bandwidth_1: Bandwidth = (
            channels[0].optical_transport_spectrum.optical_spectrum_passband[1]
            - channels[0].optical_transport_spectrum.optical_spectrum_passband[0]
        )

    if len(channels) == 1:
        return ModifyOpticalDigitalServiceForm

    class ModifyOpticalDigitalServiceDualForm(ModifyOpticalDigitalServiceForm):
        frequency_2: Frequency = channels[1].optical_transport_central_frequency
        bandwidth_2: Bandwidth = (
            channels[1].optical_transport_spectrum.optical_spectrum_passband[1]
            - channels[1].optical_transport_spectrum.optical_spectrum_passband[0]
        )

    return ModifyOpticalDigitalServiceDualForm


def modify_optical_digital_service_form_pages(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_digital_service",
) -> FormGenerator:
    """Yield the FormPage of the Optical Digital Service modify form.

    This is the shipped modify form as a page sequence: it yields the prefilled
    modify page and returns the collected user input as a flat dict of the
    ``optical_*`` state keys, consumed by the shipped steps of
    :data:`MODIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS`. Consumers yield from it
    in one line inside their own modify form generator, optionally interleaving
    their own pages. The customer of the subscription is collected separately
    by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        subscription: The ACTIVE subscription model of the Optical Digital
            Service product being modified (any consumer model that has-a the
            shipped block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Digital Service block.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield modify_optical_digital_service_form(subscription, block_field_name)
    user_input_dict = user_input.model_dump()
    for bandwidth_key in ("bandwidth_1", "bandwidth_2"):
        if user_input_dict.get(bandwidth_key) is not None and user_input_dict[bandwidth_key] % 12500 != 0:
            msg = "Bandwidth must be a multiple of 12_500 MHz"
            raise ValueError(msg)
    return user_input_dict


def modify_optical_digital_service_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalDigitalService,
    block_field_name: str = "optical_digital_service",
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Digital Service.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact. It is a thin composition of the customer
    page, the shipped page sequence
    (:func:`modify_optical_digital_service_form_pages`) and the summary form.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical
            Digital Service product. Consumers that compose the shipped block
            under a different attribute name pass their own model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Digital Service block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    block = getattr(subscription, block_field_name)

    user_input_dict = yield from customer_choice_form_page(include=str(subscription.customer_id))
    user_input_dict.update((yield from modify_optical_digital_service_form_pages(subscription, block_field_name)))

    summary_fields = ["customer_id", "optical_transport_mode", "frequency_1", "bandwidth_1"]
    if len(block.optical_digital_service_transport_channels) == 2:  # noqa: PLR2004
        summary_fields.extend(["frequency_2", "bandwidth_2"])
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
    bandwidth_1: Bandwidth,
    frequency_2: Frequency | None = None,
    bandwidth_2: Bandwidth | None = None,
) -> State:
    """Update the transport channels of the block in the state from the modify-form keys.

    Every channel keeps its ports and sections: only the central frequency, the
    passband (recomputed as ``frequency ± bandwidth / 2``) and the mode are
    overwritten. The total capacity is re-derived from the new mode on the
    service-owned channels only: reused channels keep the capacity accounting
    of their owning subscription. The old passbands are returned in the state
    so the following circuit modification step can locate the existing circuits
    on the devices.
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

    Raises:
        ValueError: If the form channel count does not match the block channel count.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    channels = list(block.optical_digital_service_transport_channels)
    new_values: list[tuple[Frequency, Bandwidth]] = [(frequency_1, bandwidth_1)]
    if frequency_2 is not None and bandwidth_2 is not None:
        new_values.append((frequency_2, bandwidth_2))
    if len(new_values) != len(channels):
        msg = "The number of carriers cannot be changed by the modify workflow"
        raise ValueError(msg)
    old_passbands: list[Passband] = []
    for channel, (frequency, bandwidth) in zip(channels, new_values, strict=True):
        old_passbands.append(channel.optical_transport_spectrum.optical_spectrum_passband)
        channel.optical_transport_central_frequency = frequency
        channel.optical_transport_spectrum.optical_spectrum_passband = (
            frequency - bandwidth // 2,
            frequency + bandwidth // 2,
        )
        channel.optical_transport_mode = optical_transport_mode
        if is_new_channel(channel, block):
            hosts = [line.optical_port_host_node for line in channel.optical_transport_line_ports]
            channel.optical_transport_total_capacity = get_transceiver_capacity_from_mode(hosts, optical_transport_mode)
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: block, "old_passbands": old_passbands}


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
        sleep(10)
    return {}


#: Modify steps operating on the Optical Digital Service block in the state. The block
#: is persisted by the last step, because workflow steps reload the subscription
#: from the database and would otherwise lose the mutations.
MODIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS: StepList = (
    begin
    >> update_optical_digital_service_block
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
    of the shipped subscription models. Only frequencies, bandwidths and mode
    are modified; endpoints, ports, paths and carrier count are fixed.
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
    "modify_optical_digital_service",
    "modify_optical_digital_service_form",
    "modify_optical_digital_service_form_generator",
    "modify_optical_digital_service_form_pages",
    "update_optical_digital_service_block",
]
