"""Create Optical Spectrum Service workflow.

This module ships the ready-to-use ``create_optical_spectrum`` workflow for the
shipped Optical Spectrum Service product type, together with the importable
parts: the FormPages of the create form (as the
:func:`create_optical_spectrum_form_pages` page sequence), the block population
logic and the step list that operates on the Optical Spectrum block found in
the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model, creates the two endpoint add/drop port blocks, populates the block with
the create-form values (the mandatory fields of the PROVISIONING lifecycle),
splits the chosen path into single-platform sections and transitions the
subscription to PROVISIONING, the shipped block steps configure the add/drop
port descriptions, deploy the optical circuit of every section, refresh the
passbands in use and persist the PROVISIONING block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``, and the shipped description step finalizes
the subscription. The shipped form generator is a thin composition of the
shipped pages and the summary form, without hooks: consumers build their own
form generator by yielding from the shipped page sequence in one line and
adding their own pages::

    user_input_dict = yield from create_optical_spectrum_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from typing import Annotated, Any, cast

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import Divider
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.hal.port import set_port_description
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlockInactive
from orchestrator.optical.products.product_blocks.optical_spectrum import OpticalSpectrumBlockInactive
from orchestrator.optical.products.product_types.optical_node.abstracts import AbstractOpticalNode
from orchestrator.optical.products.product_types.optical_spectrum_service import (
    OpticalSpectrumInactive,
    OpticalSpectrumProvisioning,
)
from orchestrator.optical.utils.custom_types.frequencies import Frequency
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_pipe.shared import multiple_optical_pipe_selector_of_types
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    LINE_SYSTEM_ROLES,
    NO_OPTICAL_PATH_FOUND_MSG,
    OPTICAL_PIPE_PRODUCT_TYPES,
    NoOpticalPathFoundError,
    check_optical_spectrum_add_drop_port_availability,
    load_ols_port,
    multiple_optical_node_selector,
    optical_node_selector_of_roles,
    optical_spectrum_block_from_state,
    optical_spectrum_path_selector,
    provision_optical_sections,
    refresh_optical_spectrum_used_passbands,
    set_optical_spectrum_subscription_description,
    split_loaded_path_into_loaded_sections,
    store_loaded_sections_into_spectrum_block,
    validate_optical_spectrum_path,
)
from orchestrator.optical.workflows.shared import create_summary_form, optical_port_selector

logger = get_logger(__name__)

ROADM_ROLES = [
    OpticalNodeRole.ROADM,
    OpticalNodeRole.TRANSPONDER_XOADM,
]

# NOTE: LINE_SYSTEM_ROLES and NO_OPTICAL_PATH_FOUND_MSG live in shared.py and are
# re-exported below for backward compatibility (import from shared going forward).


def create_optical_spectrum_identity_form(product_name: str) -> type[FormPage]:
    """Return the identity FormPage of the Optical Spectrum create form.

    This is the first page of the shipped create form: the spectrum name and the
    frequency range (passband) of the service. It is a building block for
    consumers that compose their own create form generator: the shipped page
    sequence (:func:`create_optical_spectrum_form_pages`) yields it first.

    Args:
        product_name: Name of the product being created, used as the page title.

    Returns:
        The identity FormPage of the shipped create form.
    """

    class CreateOpticalSpectrumIdentityForm(FormPage):
        model_config = ConfigDict(title=product_name)

        optical_spectrum_name: str
        frequency_min: Annotated[Frequency, Field(title="Start frequency (THz)")]
        frequency_max: Annotated[Frequency, Field(title="End frequency (THz)")]

        @model_validator(mode="after")
        def validate_frequencies(self) -> "CreateOpticalSpectrumIdentityForm":
            if self.frequency_min > self.frequency_max:
                msg = "Max frequency must be greater than min frequency. Did you make a typo?"
                raise ValueError(msg)
            return self

    return CreateOpticalSpectrumIdentityForm


def create_optical_spectrum_nodes_form(
    product_name: str,
    src_choice: type[Choice],
    dst_choice: type[Choice],
) -> type[FormPage]:
    """Return the two-nodes FormPage of the Optical Spectrum create form.

    This is the second page of the shipped create form: the two Optical Nodes the
    service connects. The page validates that the two nodes are different.

    Args:
        product_name: Name of the product being created, used as the page title.
        src_choice: The ``Choice`` selector of the source Optical Node subscriptions.
        dst_choice: The ``Choice`` selector of the destination Optical Node subscriptions.

    Returns:
        The two-nodes FormPage of the shipped create form.
    """

    class CreateOpticalSpectrumNodesForm(FormPage):
        model_config = ConfigDict(title=product_name)

        src_optical_device_id: src_choice
        dst_optical_device_id: dst_choice

        @model_validator(mode="after")
        def validate_separate_nodes(self) -> "CreateOpticalSpectrumNodesForm":
            if self.dst_optical_device_id == self.src_optical_device_id:
                msg = "Destination Optical Node cannot be the same as Source Optical Node"
                raise ValueError(msg)
            return self

    return CreateOpticalSpectrumNodesForm


def create_optical_spectrum_add_drop_form(
    product_name: str,
    src_port_choice: type[Choice],
    dst_port_choice: type[Choice],
) -> type[FormPage]:
    """Return the add/drop FormPage of the Optical Spectrum create form.

    This is the third page of the shipped create form: the device names of the
    source and destination add/drop ports. The add/drop port blocks are created
    by the shipped construct step, not by the form.

    Args:
        product_name: Name of the product being created, used as the page title.
        src_port_choice: The ``Choice`` selector of the source add/drop ports.
        dst_port_choice: The ``Choice`` selector of the destination add/drop ports.

    Returns:
        The add/drop FormPage of the shipped create form.
    """

    class CreateOpticalSpectrumAddDropForm(FormPage):
        model_config = ConfigDict(title=product_name)

        src_optical_port_name: src_port_choice
        dst_optical_port_name: dst_port_choice

    return CreateOpticalSpectrumAddDropForm


def create_optical_spectrum_waypoints_form(
    product_name: str,
    waypoints_choice: type[list[Choice]],
) -> type[FormPage]:
    """Return the waypoints FormPage of the Optical Spectrum create form.

    This is the fourth page of the shipped create form: the Optical Nodes the
    path must traverse, in order.

    Args:
        product_name: Name of the product being created, used as the page title.
        waypoints_choice: The multiple ``Choice`` selector of the waypoint nodes.

    Returns:
        The waypoints FormPage of the shipped create form.
    """

    class CreateOpticalSpectrumWaypointsForm(FormPage):
        model_config = ConfigDict(title=product_name)

        intermediate_node_ids: waypoints_choice

    return CreateOpticalSpectrumWaypointsForm


def create_optical_spectrum_constraints_form(
    product_name: str,
    exclude_nodes_choice: type[list[Choice]],
    exclude_spans_choice: type[list[Choice]],
) -> type[FormPage]:
    """Return the constraints FormPage of the Optical Spectrum create form.

    This is the fifth page of the shipped create form: the Optical Nodes and the
    fiber spans the path must not traverse.

    Args:
        product_name: Name of the product being created, used as the page title.
        exclude_nodes_choice: The multiple ``Choice`` selector of the nodes to exclude.
        exclude_spans_choice: The multiple ``Choice`` selector of the spans to exclude.

    Returns:
        The constraints FormPage of the shipped create form.
    """

    class CreateOpticalSpectrumConstraintsForm(FormPage):
        model_config = ConfigDict(title=product_name)

        exclude_devices_list: exclude_nodes_choice
        divider1: Divider
        exclude_fibers_list: exclude_spans_choice

    return CreateOpticalSpectrumConstraintsForm


def _synthetic_add_drop_port(node: AbstractOpticalNodeBlockInactive) -> OlsAddDropPortBlockInactive:
    """Build a validation-only add/drop port block on the given node.

    The create form validates the chosen path before the real add/drop port
    blocks exist, so a lightweight in-memory port block is enough to let
    :func:`split_loaded_path_into_loaded_sections` compare the endpoint platform
    with the interior ports. No database row is created.
    """
    return OlsAddDropPortBlockInactive.model_construct(
        optical_port_role=OpticalPortRole.OLS_ADD_DROP,
        optical_port_host_node=node,
    )


def create_optical_spectrum_path_form(
    path_choice: type[Choice],
    src_node: AbstractOpticalNodeBlockInactive,
    dst_node: AbstractOpticalNodeBlockInactive,
) -> type[FormPage]:
    """Return the path FormPage of the Optical Spectrum create form.

    This is the last page of the shipped create form: the optical path chosen
    among the ones computed by the path engine. The page rejects the placeholder
    option used when no path was found and validates that the chosen path can be
    split into single-platform sections, so an unsplittable path is rejected
    while the form is filled in (the construct step re-runs the same validation
    as a backstop).

    Args:
        path_choice: The ``Choice`` selector of the available optical paths.
        src_node: The source Optical Node block, used to validate the path
            against the source add/drop port platform.
        dst_node: The destination Optical Node block, used to validate the path
            against the destination add/drop port platform.

    Returns:
        The path FormPage of the shipped create form.
    """

    class CreateOpticalSpectrumPathForm(FormPage):
        model_config = ConfigDict(title="Optical Path")

        optical_path: path_choice

        @model_validator(mode="after")
        def validate_data(self) -> "CreateOpticalSpectrumPathForm":
            if self.optical_path == NO_OPTICAL_PATH_FOUND_MSG:
                msg = (
                    "No optical path found, please adjust the routing constraints "
                    "in the previous step or update fibers in the path."
                )
                raise ValueError(msg)
            try:
                validate_optical_spectrum_path(
                    self.optical_path.split(";"),
                    _synthetic_add_drop_port(src_node),
                    _synthetic_add_drop_port(dst_node),
                )
            except ValueError as exc:
                msg = f"The selected optical path cannot be split into single-platform sections: {exc}"
                raise ValueError(msg) from exc
            return self

    return CreateOpticalSpectrumPathForm


def create_optical_spectrum_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Optical Spectrum create form, in order.

    This is the shipped create form as a page sequence: it yields the identity
    page, the two-nodes page, the add/drop page, the waypoints page, the
    constraints page and the path page, and returns the collected user input as
    a flat dict of the ``optical_*`` state keys, consumed by the shipped
    construct step (:func:`construct_optical_spectrum_subscription`). The
    dependent choices are computed between the pages (the node selectors, the
    add/drop port selectors, the waypoint and exclusion selectors, and the path
    selector). The customer of the subscription is collected separately by the
    consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    node_a_choice = optical_node_selector_of_roles(
        roles=ROADM_ROLES,
        prompt="This service connects this node: ",
    )
    node_b_choice = optical_node_selector_of_roles(
        roles=ROADM_ROLES,
        prompt="...to this other node: ",
    )

    user_input_dict: dict[str, Any] = {}
    user_input_dict.update((yield create_optical_spectrum_identity_form(product_name)).model_dump())
    user_input_dict.update(
        (yield create_optical_spectrum_nodes_form(product_name, node_a_choice, node_b_choice)).model_dump()
    )

    node_a = AbstractOpticalNode.from_subscription(user_input_dict["src_optical_device_id"]).optical_node
    node_b = AbstractOpticalNode.from_subscription(user_input_dict["dst_optical_device_id"]).optical_node

    src_port_choice = optical_port_selector(
        node_a,
        roles=[OpticalPortRole.OLS_ADD_DROP],
        prompt=(
            f"Select the Add/Drop Port on {node_a.management.optical_module_node_fqdn}."
            " Please be careful to select the correct port."
        ),
    )
    dst_port_choice = optical_port_selector(
        node_b,
        roles=[OpticalPortRole.OLS_ADD_DROP],
        prompt=(
            f"Select the Add/Drop Port on {node_b.management.optical_module_node_fqdn}."
            " Please be careful to select the correct port."
        ),
    )
    user_input_dict.update(
        (yield create_optical_spectrum_add_drop_form(product_name, src_port_choice, dst_port_choice)).model_dump()
    )

    waypoints_choice = multiple_optical_node_selector(
        roles=LINE_SYSTEM_ROLES,
        prompt="Which Optical Nodes must the path pass through?",
    )
    user_input_dict.update((yield create_optical_spectrum_waypoints_form(product_name, waypoints_choice)).model_dump())

    exclude_nodes_choice = multiple_optical_node_selector(
        roles=LINE_SYSTEM_ROLES,
        prompt="Do *not* pass through these Optical Nodes",
    )
    exclude_spans_choice = multiple_optical_pipe_selector_of_types(
        OPTICAL_PIPE_PRODUCT_TYPES,
        prompt="Do *not* pass through these Optical Pipes",
    )
    user_input_dict.update(
        (
            yield create_optical_spectrum_constraints_form(product_name, exclude_nodes_choice, exclude_spans_choice)
        ).model_dump()
    )

    passband = (user_input_dict["frequency_min"], user_input_dict["frequency_max"])
    try:
        path_choice = optical_spectrum_path_selector(
            str(node_a.subscription_instance_id),
            str(node_b.subscription_instance_id),
            user_input_dict["intermediate_node_ids"],
            passband,
            user_input_dict["exclude_devices_list"],
            user_input_dict["exclude_fibers_list"],
            prompt=(
                "Select the optical path, if you don't see the desired path,"
                " adjust constraints in previous step or validate fibers along the path."
            ),
        )
    except NoOpticalPathFoundError:
        logger.exception(
            "No optical path found",
            src_optical_device_id=user_input_dict["src_optical_device_id"],
            dst_optical_device_id=user_input_dict["dst_optical_device_id"],
            passband=passband,
            exclude_devices_list=user_input_dict["exclude_devices_list"],
            exclude_fibers_list=user_input_dict["exclude_fibers_list"],
        )
        path_choice = cast(
            type[Choice],
            Choice(
                NO_OPTICAL_PATH_FOUND_MSG,
                [
                    (NO_OPTICAL_PATH_FOUND_MSG, NO_OPTICAL_PATH_FOUND_MSG),
                ],
            ),
        )

    user_input_dict.update((yield create_optical_spectrum_path_form(path_choice, node_a, node_b)).model_dump())
    user_input_dict["optical_path"] = user_input_dict["optical_path"].split(";")
    return user_input_dict


def create_optical_spectrum_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Spectrum service.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    construct step (:func:`construct_optical_spectrum_subscription`). It is a
    thin composition of the customer page, the shipped page sequence
    (:func:`create_optical_spectrum_form_pages`) and the summary form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from customer_choice_form_page(title=product_name)
    user_input_dict.update((yield from create_optical_spectrum_form_pages(product_name)))

    summary_fields = [
        "customer_id",
        "optical_spectrum_name",
        "frequency_min",
        "frequency_max",
        "src_optical_device_id",
        "dst_optical_device_id",
        "src_optical_port_name",
        "dst_optical_port_name",
        "intermediate_node_ids",
        "optical_path",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


def populate_optical_spectrum_block(
    optical_module_block: OpticalSpectrumBlockInactive,
    optical_spectrum_name: str,
    frequency_min: Frequency,
    frequency_max: Frequency,
) -> None:
    """Populate an Optical Spectrum block from the create-form state keys.

    This is the anti-corruption point for consumers that keep their own model:
    call it from their own construct step on the shipped block they compose,
    before their subscription model is transitioned to the next lifecycle.

    Args:
        optical_module_block: The Optical Spectrum block to populate (any lifecycle variant).
        optical_spectrum_name: Name of the optical spectrum.
        frequency_min: Start frequency of the passband.
        frequency_max: End frequency of the passband.
    """
    optical_module_block.optical_spectrum_name = optical_spectrum_name
    optical_module_block.optical_spectrum_passband = (frequency_min, frequency_max)


@step("Construct Optical Spectrum Subscription")
def construct_optical_spectrum_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    optical_spectrum_name: str,
    frequency_min: Frequency,
    frequency_max: Frequency,
    src_optical_device_id: UUIDstr,
    dst_optical_device_id: UUIDstr,
    src_optical_port_name: str,
    dst_optical_port_name: str,
    optical_path: list[UUIDstr],
) -> State:
    """Construct the PROVISIONING domain subscription model for an Optical Spectrum.

    This step builds the shipped ``OpticalSpectrum`` model, populates its block
    with the create-form values through :func:`populate_optical_spectrum_block`
    (the anti-corruption point), creates the two endpoint add/drop port blocks,
    splits the chosen path into single-platform sections and stores them, and
    transitions the subscription to PROVISIONING in memory, so the block found
    in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` is the PROVISIONING
    variant with its mandatory fields already set — the contract of the shipped
    block step :func:`orchestrator.optical.workflows.block.save_optical_module_block`.

    Consumers that define their own product type (composing the
    ``OpticalSpectrumBlock`` under their own attribute name) write their own
    construct step instead: it builds their subscription, populates the composed
    block with the mandatory fields set (e.g. via
    :func:`populate_optical_spectrum_block`), creates the add/drop ports, stores
    the sections, transitions it to PROVISIONING and puts the block in the state
    under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    subscription = OpticalSpectrumInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )
    populate_optical_spectrum_block(
        subscription.optical_spectrum_service,
        optical_spectrum_name,
        frequency_min,
        frequency_max,
    )

    src_device = AbstractOpticalNode.from_subscription(src_optical_device_id).optical_node
    dst_device = AbstractOpticalNode.from_subscription(dst_optical_device_id).optical_node

    check_optical_spectrum_add_drop_port_availability(
        src_device,
        src_optical_port_name,
        exclude_subscription_id=str(subscription.subscription_id),
    )
    check_optical_spectrum_add_drop_port_availability(
        dst_device,
        dst_optical_port_name,
        exclude_subscription_id=str(subscription.subscription_id),
    )

    src_port = OlsAddDropPortBlockInactive.new(
        subscription_id=subscription.subscription_id,
        optical_port_name=src_optical_port_name,
        optical_port_host_node=src_device,
        optical_port_description=(
            f"Remotely connected to {dst_device.management.optical_module_node_fqdn}"
            f" {dst_optical_port_name} via {optical_spectrum_name}. "
        ),
    )
    dst_port = OlsAddDropPortBlockInactive.new(
        subscription_id=subscription.subscription_id,
        optical_port_name=dst_optical_port_name,
        optical_port_host_node=dst_device,
        optical_port_description=(
            f"Remotely connected to {src_device.management.optical_module_node_fqdn}"
            f" {src_optical_port_name} via {optical_spectrum_name}. "
        ),
    )

    interior = [load_ols_port(port_id) for port_id in optical_path]
    sections = split_loaded_path_into_loaded_sections([src_port, *interior, dst_port])
    store_loaded_sections_into_spectrum_block(sections, subscription.optical_spectrum_service)

    subscription = OpticalSpectrumProvisioning.from_other_lifecycle(subscription, SubscriptionLifecycle.PROVISIONING)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_MODULE_BLOCK_STATE_KEY: subscription.optical_spectrum_service,
    }


@step("Adding a description to the add/drop ports")
def configure_add_drop_ports_description(optical_module_block: OpticalSpectrumBlockInactive) -> State:
    """Set the port description on the device for the source and destination add/drop ports.

    Operates only on the Optical Spectrum block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``: the block is re-hydrated from its
    serialized form (see
    :func:`orchestrator.optical.workflows.optical_spectrum_service.shared.optical_spectrum_block_from_state`)
    and the descriptions are set on the first add/drop port of the first section
    and the last add/drop port of the last section.

    Args:
        optical_module_block: The Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    sections = block.optical_spectrum_sections
    src_port = sections[0].optical_spectrum_section_add_drop_ports[0]
    dst_port = sections[-1].optical_spectrum_section_add_drop_ports[-1]

    outputs = []
    for port in (src_port, dst_port):
        command_output = set_port_description(port, port.optical_port_description or "")
        outputs.append(command_output)

    return {"configuration_results": outputs}


#: Create steps operating on the Optical Spectrum block in the state. Every step
#: is block-level: the add/drop port descriptions are configured on the devices,
#: the optical circuit of every section is deployed, the passbands in use are
#: refreshed and the block (with the refreshed passbands) is persisted by the
#: last step, because workflow steps execute with the state serialized between
#: steps (the block is re-hydrated from its serialized form before every step
#: operates on it). The block is assumed to be in the PROVISIONING lifecycle
#: status with its mandatory fields and sections already set: the caller's
#: construct step provides it (see
#: :func:`construct_optical_spectrum_subscription`). Consumers with their own
#: model run this list after constructing their subscription the same way and
#: putting their block in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
#: The device-push, passband-refresh and verification steps are shared with the
#: other shipped spectrum workflows (see
#: :mod:`orchestrator.optical.workflows.optical_spectrum_service.shared`).
CREATE_OPTICAL_SPECTRUM_BLOCK_STEPS: StepList = (
    begin
    >> configure_add_drop_ports_description
    >> provision_optical_sections
    >> refresh_optical_spectrum_used_passbands
    >> save_optical_module_block
)


@create_workflow(initial_input_form=create_optical_spectrum_form_generator)
def create_optical_spectrum() -> StepList:
    """Workflow to create a new Optical Spectrum service subscription.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalSpectrum` model, creates the add/drop port blocks,
    stores the sections and transitions the subscription to PROVISIONING, the
    shipped block steps configure the devices and persist the block, and the
    shipped description step finalizes the subscription. It is therefore only
    valid for the shipped product type; consumers with their own product type
    compose their own create workflow with the same parts.
    """
    return (
        begin
        >> construct_optical_spectrum_subscription
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> CREATE_OPTICAL_SPECTRUM_BLOCK_STEPS
        >> set_optical_spectrum_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_OPTICAL_SPECTRUM_BLOCK_STEPS",
    "LINE_SYSTEM_ROLES",
    "NO_OPTICAL_PATH_FOUND_MSG",
    "construct_optical_spectrum_subscription",
    "create_optical_spectrum",
    "create_optical_spectrum_form_generator",
    "create_optical_spectrum_form_pages",
    "populate_optical_spectrum_block",
]
