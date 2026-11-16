"""Modify Optical Leased Spectrum workflow.

This module ships the ready-to-use ``modify_leased_spectrum`` workflow for
the shipped Optical Leased Spectrum product type, together with the
importable parts: the FormPage of the modify form (as the
:func:`modify_leased_spectrum_form_pages` page sequence, prefilled with the
current block values) and the step list that updates and persists the
Optical Leased Spectrum block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages. The consumer extracts the
block with plain Python at any nesting depth (shipped code never traverses
the subscription)::

    block = subscription.optical_module_block  # or subscription.router.optical_module
    user_input_dict = yield from modify_leased_spectrum_form_pages(block)
    user_input_dict.update((yield my_own_page).model_dump())

Besides the pipe name, the page collects the leased passbands
(``leased_passbands``, the frequency ranges typed in THz, prefilled with the
stored ones): they limit the frequencies offered to the services routed through
the pipe from then on. Services already routed through the pipe are not checked
against a narrower lease.
"""

from typing import cast

from pydantic import Field, field_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_blocks.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumBlock,
    OpticalLeasedSpectrumBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import OpticalLeasedSpectrumSubscription
from orchestrator.optical.utils.custom_types.frequencies import parse_passbands_thz, passbands_to_thz_text
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_pipe.leased_spectrum.create_leased_spectrum import (
    leased_passbands_field,
    normalize_leased_passbands,
)
from orchestrator.optical.workflows.optical_pipe.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    default_pipe_identifier_of,
    load_optical_pipe_block,
    optical_pipe_block_from_state,
    set_optical_pipe_subscription_description,
    update_optical_pipe_block,
)
from orchestrator.optical.workflows.shared import modify_summary_form, retryable_form


def modify_leased_spectrum_form(pipe: OpticalLeasedSpectrumBlock) -> type[FormPage]:
    """Return the modify FormPage of an Optical Leased Spectrum pipe.

    The page is prefilled with the current ``optical_pipe_name`` and leased
    passbands of the block, so unchanged fields remain intact. The name may be
    left empty to go back to the default identifier; the leased passbands may be
    emptied to lift the restriction.

    Args:
        pipe: The Optical Leased Spectrum block being modified.

    Returns:
        The prefilled modify FormPage of the shipped modify form.
    """

    class ModifyLeasedSpectrumForm(FormPage):
        optical_pipe_name: str | None = Field(
            pipe.optical_pipe_name,
            title="Pipe Identifier",
            description="Unique pipe ID or code. Leave empty to use the default 'node A port A --- node B port B'.",
        )
        leased_passbands: str = leased_passbands_field(passbands_to_thz_text(pipe.optical_leased_passbands))

        _normalize_leased_passbands = field_validator("leased_passbands")(normalize_leased_passbands)

    return ModifyLeasedSpectrumForm


def modify_leased_spectrum_form_pages(pipe: OpticalLeasedSpectrumBlock) -> FormGenerator:
    """Yield the FormPage of the Optical Leased Spectrum modify form.

    This is the shipped modify form as a page sequence: it yields the prefilled
    modify page (:func:`modify_leased_spectrum_form`) and returns the collected
    user input as a flat dict (``optical_pipe_name``, where an empty name becomes
    the default identifier of the pipe, and ``leased_passbands``), consumed by the
    shipped steps of
    :data:`MODIFY_LEASED_SPECTRUM_BLOCK_STEPS`. Consumers yield from it in one
    line inside their own modify form generator, optionally interleaving their
    own pages. The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        pipe: The Optical Leased Spectrum block being modified.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input_dict = (yield modify_leased_spectrum_form(pipe)).model_dump()
    name = (user_input_dict["optical_pipe_name"] or "").strip()
    user_input_dict["optical_pipe_name"] = name or default_pipe_identifier_of(pipe)
    return user_input_dict


@retryable_form
def modify_leased_spectrum_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalLeasedSpectrumSubscription,
    block_field_name: str = "optical_pipe",
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Leased Spectrum subscription.

    The form is prefilled with the current values of the block, so
    unchanged fields remain intact. It is a thin composition of the customer
    page, the shipped page sequence
    (:func:`modify_leased_spectrum_form_pages`) and the summary form.
    Shipped-product only: consumers compose their own form
    generator from the shipped page sequence.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical
            Leased Spectrum product.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Leased Spectrum block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    pipe = getattr(subscription, block_field_name)

    user_input_dict = yield from customer_choice_form_page(include=subscription.customer_id)
    user_input_dict.update((yield from modify_leased_spectrum_form_pages(pipe)))

    yield from modify_summary_form(
        user_input_dict,
        pipe,
        ["customer_id", "optical_pipe_name", "leased_passbands"],
        extra_before={
            "customer_id": subscription.customer_id,
            "leased_passbands": passbands_to_thz_text(pipe.optical_leased_passbands),
        },
    )

    return user_input_dict | {"subscription": subscription}


@step("Updating the leased passbands")
def update_leased_spectrum_passbands(
    optical_module_block: OpticalLeasedSpectrumBlockProvisioning,
    leased_passbands: str = "",
) -> State:
    """Write the leased passbands of the modify form to the Optical Leased Spectrum block in the state.

    Args:
        optical_module_block: The Optical Leased Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY`` (the provisioning variant, while the
            subscription is being modified).
        leased_passbands: The leased frequency ranges typed in THz (see
            :func:`orchestrator.optical.utils.custom_types.frequencies.parse_passbands_thz`);
            empty when the lease is not restricted.
    """
    pipe_block = cast(OpticalLeasedSpectrumBlockProvisioning, optical_pipe_block_from_state(optical_module_block))
    pipe_block.optical_leased_passbands = parse_passbands_thz(leased_passbands)
    return {OPTICAL_MODULE_BLOCK_STATE_KEY: pipe_block}


#: Modify steps operating on the Optical Leased Spectrum block in the state.
#: The ``optical_pipe_name`` and the ``optical_leased_passbands`` are written to
#: the block; the block is persisted by the last step, because workflow steps
#: reload the subscription from the database and would otherwise lose the mutations.
MODIFY_LEASED_SPECTRUM_BLOCK_STEPS: StepList = (
    begin >> update_optical_pipe_block >> update_leased_spectrum_passbands >> save_optical_module_block
)


@modify_workflow(initial_input_form=modify_leased_spectrum_form_generator)
def modify_leased_spectrum() -> StepList:
    """Workflow to modify an existing Optical Leased Spectrum pipe.

    The workflow is valid for the shipped :class:`OpticalLeasedSpectrum`
    product type only: it loads the block from the ``optical_pipe`` attribute
    of the shipped subscription models. Consumers with their own product type
    compose their own modify workflow with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_pipe_block
        >> MODIFY_LEASED_SPECTRUM_BLOCK_STEPS
        >> set_optical_pipe_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_LEASED_SPECTRUM_BLOCK_STEPS",
    "modify_leased_spectrum",
    "modify_leased_spectrum_form",
    "modify_leased_spectrum_form_pages",
    "update_leased_spectrum_passbands",
]
