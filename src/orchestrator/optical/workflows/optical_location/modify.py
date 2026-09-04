"""Modify Optical Module Location workflow.

This module ships the ready-to-use ``modify_optical_module_location``
workflow for the shipped Optical Module Location product type, together
with the importable parts: the FormPages of the modify form (as the
:func:`modify_optical_module_location_form_pages` page sequence, prefilled
with the current subscription values) and the step list that updates and
persists the Optical Module Location block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``. The workflow also refreshes the
subscription description from the updated block (falling back to the
location code only when the optional location name is cleared).

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks:
consumers build their own form generator by yielding from the shipped page
sequence in one line and adding their own pages. When the block is not a
direct attribute of the subscription (for example, when it is nested under one
of the consumer's own product blocks), the consumer passes the block
explicitly::

    user_input_dict = yield from modify_optical_module_location_form_pages(
        subscription, location=subscription.router.for_the_optical_module
    )
    user_input_dict.update((yield my_own_page).model_dump())
"""

from typing import Annotated, cast

from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_blocks.optical_location import (
    LocationCode,
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_location import OpticalModuleLocationSubscription
from orchestrator.optical.utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_location.shared import (
    OPTICAL_MODULE_BLOCK_STATE_KEY,
    check_location_code_uniqueness,
    load_optical_module_location_block,
    optical_location_block_from_state,
    save_optical_module_location_block,
    set_optical_module_location_subscription_description,
)
from orchestrator.optical.workflows.shared import modify_summary_form

Instruction = Annotated[
    str,
    Field(
        "Modify the location fields. Unchanged fields will remain intact. "
        "Tick the 'clear location name' checkbox to remove the optional location name.",
        title="Instruction",
        json_schema_extra={"disabled": True},
    ),
]


def modify_optical_module_location_form(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_location",
    location: OpticalModuleLocationBlock | None = None,
) -> type[FormPage]:
    """Return the modify FormPage of the Optical Module Location subscription.

    The page is prefilled with the current values of the subscription, so
    unchanged fields remain intact. The optional ``location_name`` field can be
    deleted by ticking the ``clear_location_name`` checkbox. The page validates
    that the entered ``location_code`` is not already in use by another
    location subscription, excluding the subscription being modified.

    Args:
        subscription: The ACTIVE subscription model of the Optical Module
            Location product being modified (any consumer model that has-a the
            shipped block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Module Location block.
        location: The Optical Module Location block, when it is not available
            under the ``block_field_name`` attribute. Consumer models that
            compose the block deeper (for example under one of their own product
            blocks) pass the block explicitly.

    Returns:
        The prefilled modify FormPage of the shipped modify form.
    """
    location = location or cast(OpticalModuleLocationBlock, getattr(subscription, block_field_name))

    class ModifyOpticalModuleLocationForm(FormPage):
        instruction: Instruction
        longitude: Annotated[
            LongitudeCoordinate,
            Field(title="Longitude", description="Longitude of the location, between -180 and +180 degrees."),
        ] = location.longitude
        latitude: Annotated[
            LatitudeCoordinate,
            Field(title="Latitude", description="Latitude of the location, between -90 and +90 degrees."),
        ] = location.latitude
        location_code: Annotated[
            LocationCode,
            Field(
                title="Location Code",
            ),
        ] = location.location_code
        location_name: str | None = Field(
            location.location_name,
            title="Location Name",
            description="Human-readable name of the location, e.g. 'Amsterdam'.",
        )
        clear_location_name: bool = Field(
            default=False,
            title="Clear location name",
            description="Tick to remove the location name from the subscription.",
        )

        @model_validator(mode="after")
        def validate_unique_location_code(self) -> "ModifyOpticalModuleLocationForm":
            """Raise if the entered location code is already in use by another subscription."""
            check_location_code_uniqueness(
                self.location_code, exclude_subscription_id=str(subscription.subscription_id)
            )
            return self

    return ModifyOpticalModuleLocationForm


def modify_optical_module_location_form_pages(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_location",
    location: OpticalModuleLocationBlock | None = None,
) -> FormGenerator:
    """Yield the FormPage of the Optical Module Location modify form.

    This is the shipped modify form as a page sequence: it yields the prefilled
    modify page and returns the collected user input as a flat dict of the
    ``optical_*`` state keys, consumed by the shipped steps of
    :data:`MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS`. Consumers yield from
    it in one line inside their own modify form generator, optionally
    interleaving their own pages. The customer of the subscription is
    collected separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        subscription: The ACTIVE subscription model of the Optical Module
            Location product being modified (any consumer model that has-a the
            shipped block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Module Location block.
        location: The Optical Module Location block, when it is not available
            under the ``block_field_name`` attribute. Consumer models that
            compose the block deeper (for example under one of their own product
            blocks) pass the block explicitly.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input = yield modify_optical_module_location_form(subscription, block_field_name, location)
    return user_input.model_dump()


def modify_optical_module_location_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalModuleLocationSubscription,
    block_field_name: str = "optical_location",
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Module Location subscription.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact. It is a thin composition of the shipped
    page sequence (:func:`modify_optical_module_location_form_pages`) and the
    summary form.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical
            Module Location product. Consumers that compose the shipped block
            under a different attribute name pass their own model class when they
            call this generator from their own form generator (a thin wrapper that
            yields from it; pre-binding with ``functools.partial`` is not supported
            by the core form-argument injection, which passes the bound parameters
            positionally from their signature defaults).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Module Location block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    location = getattr(subscription, block_field_name)

    user_input_dict = yield from customer_choice_form_page(include=subscription.customer_id)
    user_input_dict.update((yield from modify_optical_module_location_form_pages(subscription, block_field_name)))

    summary_fields = [
        "customer_id",
        "longitude",
        "latitude",
        "location_code",
        "location_name",
    ]
    yield from modify_summary_form(
        user_input_dict,
        location,
        summary_fields,
        extra_before={"customer_id": subscription.customer_id},
    )

    return user_input_dict | {"subscription": subscription}


@step("Updating Optical Module Location block")
def update_optical_module_location_block(
    optical_module_block: OpticalModuleLocationBlockProvisioning,
    longitude: LongitudeCoordinate,
    latitude: LatitudeCoordinate,
    location_code: LocationCode,
    location_name: str | None,
    clear_location_name: bool = False,  # noqa: FBT001, FBT002
) -> State:
    """Update the Optical Module Location block in the state from the modify-form keys.

    All fields are overwritten with the form values; the optional
    ``location_name`` is removed when the ``clear_location_name`` checkbox is
    ticked. The step re-checks the uniqueness of the ``location_code`` at
    execution time, excluding the subscription being modified, so consumers
    bypassing the form validation are still guarded against duplicates.
    Workflow steps execute with the state serialized between steps, so
    the block is re-hydrated from the database by its ``subscription_instance_id``
    before it is updated.

    Args:
        optical_module_block: The Optical Module Location block
            in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``
            (the provisioning variant, while the subscription is being modified).
        longitude: Longitude of the location.
        latitude: Latitude of the location.
        location_code: Code of the location.
        location_name: Human-readable name of the location.
        clear_location_name: Whether to remove the location name.

    Raises:
        ValueError: If the location code is already in use by another subscription.
    """
    location_block = optical_location_block_from_state(optical_module_block)
    check_location_code_uniqueness(location_code, exclude_subscription_id=str(location_block.owner_subscription_id))
    location_block.longitude = longitude
    location_block.latitude = latitude
    location_block.location_code = location_code
    location_block.location_name = None if clear_location_name else location_name

    return {OPTICAL_MODULE_BLOCK_STATE_KEY: location_block}


#: Modify steps operating on the Optical Module Location block in the state.
#: The block is persisted by the last step, because workflow steps reload the
#: subscription from the database and would otherwise lose the mutations.
MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS: StepList = (
    begin >> update_optical_module_location_block >> save_optical_module_location_block
)


@modify_workflow(initial_input_form=modify_optical_module_location_form_generator)
def modify_optical_module_location() -> StepList:
    """Workflow to modify an existing Optical Module Location subscription.

    The workflow is valid for the shipped :class:`OpticalModuleLocationSubscription`
    product type only: it loads the block from the ``optical_location``
    attribute of the shipped subscription models. The shipped description step
    refreshes the subscription description from the updated block: when the
    optional location name is cleared, the description falls back to the
    location code only. Consumers with their own product type compose their own
    modify workflow with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_module_location_block
        >> MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS
        >> set_optical_module_location_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_OPTICAL_MODULE_LOCATION_BLOCK_STEPS",
    "modify_optical_module_location",
    "modify_optical_module_location_form_pages",
    "update_optical_module_location_block",
]
