"""Create Optical Module Location workflow.

This module ships the ready-to-use ``create_optical_module_location``
workflow for the shipped Optical Module Location product type, together
with the importable parts: the FormPages of the create form (as the
:func:`create_optical_module_location_form_pages` page sequence), the block
population logic and the step list that operates on the Optical Module
Location block found in the state under ``OPTICAL_LOCATION_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model and puts its block in the state, the shipped block steps populate and
persist the block, and the shipped description step finalizes the
subscription. The shipped form generator is a thin composition of the shipped
pages and the summary form, without hooks: consumers build their own form
generator by yielding from the shipped page sequence in one line and adding
their own pages::

    user_input_dict = yield from create_optical_module_location_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from typing import Annotated

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.products.product_blocks.optical_location import (
    LocationCode,
    OpticalModuleLocationBlockInactive,
)
from orchestrator.optical.products.product_types.optical_location import OpticalModuleLocationSubscriptionInactive
from orchestrator.optical.utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_location.shared import (
    OPTICAL_LOCATION_BLOCK_STATE_KEY,
    check_location_code_uniqueness,
    optical_location_block_from_state,
    save_optical_module_location_block,
    set_optical_module_location_subscription_description,
)
from orchestrator.optical.workflows.shared import create_summary_form


def create_optical_module_location_identity_form(product_name: str) -> type[FormPage]:
    """Return the identity FormPage of the Optical Module Location create form.

    This is the first page of the shipped create form: the code and the
    human-readable name of the location. It is a building block for consumers
    that compose their own create form generator: the shipped page sequence
    (:func:`create_optical_module_location_form_pages`) yields it first. The
    page validates that the entered ``location_code`` is not already in use by
    another location subscription.

    Args:
        product_name: Name of the product being created, used as the page title.

    Returns:
        The identity FormPage of the shipped create form.
    """

    class CreateOpticalModuleLocationIdentityForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Identity")

        location_code: Annotated[
            LocationCode,
            Field(
                title="Location Code",
            ),
        ]
        location_name: str | None = Field(
            None,
            title="Location Name",
            description="Human-readable name of the location, e.g. 'Amsterdam'.",
        )

        @model_validator(mode="after")
        def validate_unique_location_code(self) -> "CreateOpticalModuleLocationIdentityForm":
            """Raise if the entered location code is already in use by another subscription."""
            check_location_code_uniqueness(self.location_code)
            return self

    return CreateOpticalModuleLocationIdentityForm


def create_optical_module_location_coordinates_form(product_name: str) -> type[FormPage]:
    """Return the coordinates FormPage of the Optical Module Location create form.

    This is the second page of the shipped create form: the coordinates of the
    location. It is a building block for consumers that compose their own
    create form generator: the shipped page sequence
    (:func:`create_optical_module_location_form_pages`) yields it second.

    Args:
        product_name: Name of the product being created, used as the page title.

    Returns:
        The coordinates FormPage of the shipped create form.
    """

    class CreateOpticalModuleLocationCoordinatesForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Coordinates")

        longitude: Annotated[
            LongitudeCoordinate,
            Field(title="Longitude", description="Longitude of the location, between -180 and +180 degrees."),
        ]
        latitude: Annotated[
            LatitudeCoordinate,
            Field(title="Latitude", description="Latitude of the location, between -90 and +90 degrees."),
        ]

    return CreateOpticalModuleLocationCoordinatesForm


def create_optical_module_location_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Optical Module Location create form, in order.

    This is the shipped create form as a page sequence: it yields the
    identity page and the coordinates page, and returns the collected user
    input as a flat dict of the ``optical_*`` state keys, consumed by the
    shipped steps of :data:`CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS`.
    Consumers yield from it in one line inside their own create form generator,
    optionally interleaving their own pages. The customer of the subscription
    is collected separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input_dict: dict[str, str | None] = {}
    user_input_dict.update((yield create_optical_module_location_identity_form(product_name)).model_dump())
    user_input_dict.update((yield create_optical_module_location_coordinates_form(product_name)).model_dump())
    return user_input_dict


def create_optical_module_location_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Module Location.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    steps of :data:`CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS`. It is a thin
    composition of the shipped page sequence
    (:func:`create_optical_module_location_form_pages`) and the summary form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from customer_choice_form_page(title=product_name)
    user_input_dict.update((yield from create_optical_module_location_form_pages(product_name)))

    summary_fields = [
        "customer_id",
        "location_code",
        "location_name",
        "longitude",
        "latitude",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


def populate_optical_module_location_block(
    optical_module_location_block: OpticalModuleLocationBlockInactive,
    longitude: LongitudeCoordinate,
    latitude: LatitudeCoordinate,
    location_code: LocationCode,
    location_name: str | None = None,
) -> None:
    """Populate an Optical Module Location block from the create-form state keys.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step on the shipped block they compose,
    before their subscription model is transitioned to the next lifecycle. It
    re-checks the uniqueness of the ``location_code`` at execution time, so
    consumers bypassing the form validation are still guarded against
    duplicates.

    Args:
        optical_module_location_block: The Optical Module Location block to populate (any lifecycle variant).
        longitude: Longitude of the location.
        latitude: Latitude of the location.
        location_code: Code of the location.
        location_name: Human-readable name of the location.

    Raises:
        ValueError: If the location code is already in use by another subscription.
    """
    check_location_code_uniqueness(
        location_code,
        exclude_subscription_id=str(optical_module_location_block.owner_subscription_id),
    )
    optical_module_location_block.longitude = longitude
    optical_module_location_block.latitude = latitude
    optical_module_location_block.location_code = location_code
    optical_module_location_block.location_name = location_name


@step("Populate Optical Module Location block")
def populate_optical_module_location_block_step(
    optical_module_location_block: OpticalModuleLocationBlockInactive,
    longitude: LongitudeCoordinate,
    latitude: LatitudeCoordinate,
    location_code: LocationCode,
    location_name: str | None = None,
) -> State:
    """Populate the Optical Module Location block found in the state from the create-form keys.

    Workflow steps execute with the state serialized between steps, so the
    block is re-hydrated from the database by its ``subscription_instance_id``
    before it is populated.

    Args:
        optical_module_location_block: The Optical Module Location block
            in the state under ``OPTICAL_LOCATION_BLOCK_STATE_KEY``.
        longitude: Longitude of the location.
        latitude: Latitude of the location.
        location_code: Code of the location.
        location_name: Human-readable name of the location.
    """
    location_block = optical_location_block_from_state(optical_module_location_block)
    if location_block is None:
        msg = "No Optical Module Location block in the state under OPTICAL_LOCATION_BLOCK_STATE_KEY"
        raise ValueError(msg)
    populate_optical_module_location_block(
        optical_module_location_block=location_block,
        longitude=longitude,
        latitude=latitude,
        location_code=location_code,
        location_name=location_name,
    )
    return {OPTICAL_LOCATION_BLOCK_STATE_KEY: location_block}


@step("Construct Subscription model")
def construct_optical_module_location_subscription(product: UUIDstr, customer_id: UUIDstr) -> State:
    """Construct the initial domain subscription model for an Optical Module Location.

    This step builds the shipped ``OpticalModuleLocationSubscription`` model
    and puts its block in the state under ``OPTICAL_LOCATION_BLOCK_STATE_KEY``
    for the shipped block steps of
    :data:`CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS`. Consumers that define
    their own product type (composing the ``OpticalModuleLocationBlock`` under
    their own attribute name) write their own construct step instead and can
    reuse :func:`populate_optical_module_location_block` as the
    anti-corruption point between their model and the shipped block.
    """
    subscription = OpticalModuleLocationSubscriptionInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_LOCATION_BLOCK_STATE_KEY: subscription.optical_location,
    }


#: Create steps operating on the Optical Module Location block in the state.
#: The block is re-hydrated from the database and persisted by the last step,
#: because workflow steps execute with the state serialized between steps.
#: Consumers with their own model run this list after constructing their
#: (inactive) subscription and putting their block in the state under
#: ``OPTICAL_LOCATION_BLOCK_STATE_KEY``.
CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS: StepList = (
    begin >> populate_optical_module_location_block_step >> save_optical_module_location_block
)


@create_workflow(initial_input_form=create_optical_module_location_form_generator)
def create_optical_module_location() -> StepList:
    """Workflow to create a new Optical Module Location subscription.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalModuleLocationSubscription` model and puts its
    block in the state, the shipped block steps populate and persist the
    block, and the shipped description step finalizes the subscription. It is
    therefore only valid for the shipped product type; consumers with their
    own product type compose their own create workflow with the same parts.
    """
    return (
        begin
        >> construct_optical_module_location_subscription
        >> CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> set_optical_module_location_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_OPTICAL_MODULE_LOCATION_BLOCK_STEPS",
    "create_optical_module_location",
    "create_optical_module_location_form_pages",
    "populate_optical_module_location_block",
]
