"""Modify Optical Spectrum Service workflow.

This module ships the ready-to-use ``modify_optical_spectrum`` workflow for the
shipped Optical Spectrum Service product type, together with the importable
parts: the FormPages of the modify form (as the
:func:`modify_optical_spectrum_form_pages` page sequence, prefilled with the
current subscription values) and the step list that updates and persists the
Optical Spectrum block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``. The source and destination add/drop port
blocks are reused from the existing sections, so the form only collects the
identity, the ordered waypoints, the routing constraints and the new optical
path; the path is recomputed between the existing source and destination nodes.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@modify_workflow`` with the parts. The shipped form generator is a thin
composition of the shipped pages and the summary form, without hooks: consumers
build their own form generator by yielding from the shipped page sequence in
one line and adding their own pages::

    user_input_dict = yield from modify_optical_spectrum_form_pages(
        subscription, block_field_name="optical_spectrum_service"
    )
    user_input_dict.update((yield my_own_page).model_dump())
"""

from typing import Annotated, Any, cast

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import Divider
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.hal.adapters.nokia_flexils.spectrum import FLEXILS_SPECTRAL_GRID_MHZ
from orchestrator.optical.hal.spectrum import ensure_optical_circuit
from orchestrator.optical.products.product_blocks.optical_port.abstracts import AbstractOpticalOlsPortBlockInactive
from orchestrator.optical.products.product_blocks.optical_spectrum import OpticalSpectrumServiceBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_spectrum_service import OpticalSpectrumServiceSubscription
from orchestrator.optical.utils.custom_types.frequencies import (
    Frequency,
    Passband,
    ensure_passband_aligned_to_grid,
    snap_passband_to_grid,
)
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_pipe.shared import multiple_optical_pipe_selector_of_types
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    LINE_SYSTEM_ROLES,
    NO_OPTICAL_PATH_FOUND_MSG,
    OPTICAL_PIPE_PRODUCT_TYPES,
    NoOpticalPathFoundError,
    delete_optical_spectrum_sections,
    load_ols_port,
    load_optical_spectrum_block,
    load_spectrum_section,
    multiple_optical_node_selector,
    optical_spectrum_block_from_state,
    optical_spectrum_path_selector,
    refresh_optical_spectrum_used_passbands,
    set_optical_spectrum_subscription_description,
    split_loaded_path_into_loaded_sections,
    store_loaded_sections_into_spectrum_block,
    validate_optical_spectrum_path,
)
from orchestrator.optical.workflows.shared import modify_summary_form

logger = get_logger(__name__)

# NOTE: LINE_SYSTEM_ROLES lives in shared.py; re-exported via __all__ below for
# backward compatibility (import from shared going forward).


def modify_optical_spectrum_identity_form(
    product_name: str,
    old_name: str,
    old_passband: Passband,
) -> type[FormPage]:
    """Return the identity FormPage of the Optical Spectrum modify form.

    This is the first page of the shipped modify form: the spectrum name and the
    frequency range (passband) of the service, prefilled with the current values
    so unchanged fields remain intact.

    Args:
        product_name: Name of the product being modified, used as the page title.
        old_name: The current name of the optical spectrum.
        old_passband: The current passband of the optical spectrum.

    Returns:
        The identity FormPage of the shipped modify form.
    """

    class ModifyOpticalSpectrumIdentityForm(FormPage):
        model_config = ConfigDict(title=product_name)

        optical_spectrum_name: str = old_name
        frequency_min: Annotated[Frequency, Field(title="Start frequency (THz)")] = old_passband[0]
        frequency_max: Annotated[Frequency, Field(title="End frequency (THz)")] = old_passband[1]

        @model_validator(mode="after")
        def validate_frequencies(self) -> "ModifyOpticalSpectrumIdentityForm":
            if self.frequency_min > self.frequency_max:
                msg = "Max frequency must be greater than min frequency. Did you make a typo?"
                raise ValueError(msg)
            ensure_passband_aligned_to_grid((self.frequency_min, self.frequency_max), FLEXILS_SPECTRAL_GRID_MHZ)
            return self

    return ModifyOpticalSpectrumIdentityForm


def modify_optical_spectrum_waypoints_form(
    product_name: str,
    waypoints_choice: type[list[Choice]],
) -> type[FormPage]:
    """Return the waypoints FormPage of the Optical Spectrum modify form.

    This is the second page of the shipped modify form: the Optical Nodes the
    new path must traverse, in order.

    Args:
        product_name: Name of the product being modified, used as the page title.
        waypoints_choice: The multiple ``Choice`` selector of the waypoint nodes.

    Returns:
        The waypoints FormPage of the shipped modify form.
    """

    class ModifyOpticalSpectrumWaypointsForm(FormPage):
        model_config = ConfigDict(title=product_name)

        intermediate_node_instance_ids: waypoints_choice

    return ModifyOpticalSpectrumWaypointsForm


def modify_optical_spectrum_constraints_form(
    product_name: str,
    exclude_nodes_choice: type[list[Choice]],
    exclude_spans_choice: type[list[Choice]],
) -> type[FormPage]:
    """Return the constraints FormPage of the Optical Spectrum modify form.

    This is the third page of the shipped modify form: the Optical Nodes and the
    fiber spans the new path must not traverse.

    Args:
        product_name: Name of the product being modified, used as the page title.
        exclude_nodes_choice: The multiple ``Choice`` selector of the nodes to exclude.
        exclude_spans_choice: The multiple ``Choice`` selector of the spans to exclude.

    Returns:
        The constraints FormPage of the shipped modify form.
    """

    class ModifyOpticalSpectrumConstraintsForm(FormPage):
        model_config = ConfigDict(title=product_name)

        exclude_node_instance_ids: exclude_nodes_choice
        divider1: Divider
        exclude_pipe_instance_ids: exclude_spans_choice

    return ModifyOpticalSpectrumConstraintsForm


def modify_optical_spectrum_path_form(
    path_choice: type[Choice],
    src_endpoint: AbstractOpticalOlsPortBlockInactive,
    dst_endpoint: AbstractOpticalOlsPortBlockInactive,
) -> type[FormPage]:
    """Return the path FormPage of the Optical Spectrum modify form.

    This is the last page of the shipped modify form: the optical path chosen
    among the ones computed by the path engine. The page rejects the placeholder
    option used when no path was found and validates that the chosen path can be
    split into single-platform sections, so an unsplittable path is rejected
    while the form is filled in (the divide step re-runs the same validation as a
    backstop).

    Args:
        path_choice: The ``Choice`` selector of the available optical paths.
        src_endpoint: The existing source add/drop port block, reused by the
            modify workflow.
        dst_endpoint: The existing destination add/drop port block, reused by the
            modify workflow.

    Returns:
        The path FormPage of the shipped modify form.
    """

    class ModifyOpticalSpectrumPathForm(FormPage):
        model_config = ConfigDict(title="Optical Path")

        optical_path: path_choice

        @model_validator(mode="after")
        def validate_data(self) -> "ModifyOpticalSpectrumPathForm":
            if self.optical_path == NO_OPTICAL_PATH_FOUND_MSG:
                msg = (
                    "No optical path found, please adjust the routing constraints "
                    "in the previous step or update fibers in the path."
                )
                raise ValueError(msg)
            try:
                validate_optical_spectrum_path(
                    self.optical_path.split(";"),
                    src_endpoint,
                    dst_endpoint,
                )
            except ValueError as exc:
                msg = f"The selected optical path cannot be split into single-platform sections: {exc}"
                raise ValueError(msg) from exc
            return self

    return ModifyOpticalSpectrumPathForm


def modify_optical_spectrum_form_pages(
    subscription: SubscriptionModel,
    block_field_name: str = "optical_spectrum_service",
) -> FormGenerator:
    """Yield the FormPages of the Optical Spectrum modify form, in order.

    This is the shipped modify form as a page sequence: it yields the identity
    page, the waypoints page, the constraints page and the path page, and returns
    the collected user input as a flat dict of the ``optical_*`` state keys,
    consumed by the shipped block steps of
    :data:`MODIFY_OPTICAL_SPECTRUM_BLOCK_STEPS`. The source and destination
    add/drop port blocks are reused from the existing sections: the path is
    recomputed between the existing source and destination nodes, with the
    ordered waypoints and the exclusions collected by the form. Consumers yield
    from it in one line inside their own modify form generator, optionally
    interleaving their own pages. The customer of the subscription is collected
    separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        subscription: The ACTIVE subscription model of the Optical Spectrum
            product being modified (any consumer model that has-a the shipped
            block works).
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Spectrum block.

    Returns:
        The collected user input of the shipped pages.
    """
    block = getattr(subscription, block_field_name)
    product_name = subscription.product.name
    old_name = block.optical_spectrum_name
    old_passband = block.optical_spectrum_passband

    sections = block.optical_spectrum_sections
    src_endpoint = sections[0].optical_spectrum_section_add_drop_ports[0]
    dst_endpoint = sections[-1].optical_spectrum_section_add_drop_ports[-1]
    src_node = src_endpoint.optical_port_host_node
    dst_node = dst_endpoint.optical_port_host_node

    user_input_dict: dict[str, Any] = {}
    user_input_dict.update(
        (yield modify_optical_spectrum_identity_form(product_name, old_name, old_passband)).model_dump()
    )

    waypoints_choice = multiple_optical_node_selector(
        roles=LINE_SYSTEM_ROLES,
        prompt="Which Optical Nodes must the path pass through?",
    )
    user_input_dict.update((yield modify_optical_spectrum_waypoints_form(product_name, waypoints_choice)).model_dump())

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
            yield modify_optical_spectrum_constraints_form(product_name, exclude_nodes_choice, exclude_spans_choice)
        ).model_dump()
    )

    passband = (user_input_dict["frequency_min"], user_input_dict["frequency_max"])
    try:
        path_choice = optical_spectrum_path_selector(
            str(src_node.subscription_instance_id),
            str(dst_node.subscription_instance_id),
            user_input_dict["intermediate_node_instance_ids"],
            passband,
            user_input_dict["exclude_node_instance_ids"],
            user_input_dict["exclude_pipe_instance_ids"],
            prompt=(
                "Select the optical path, if you don't see the desired path,"
                " adjust constraints in previous step or validate fibers along the path."
            ),
        )
    except NoOpticalPathFoundError:
        logger.exception(
            "No optical path found",
            src_optical_node_instance_id=str(src_node.subscription_instance_id),
            dst_optical_node_instance_id=str(dst_node.subscription_instance_id),
            passband=passband,
            exclude_node_instance_ids=user_input_dict["exclude_node_instance_ids"],
            exclude_pipe_instance_ids=user_input_dict["exclude_pipe_instance_ids"],
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

    user_input_dict.update(
        (yield modify_optical_spectrum_path_form(path_choice, src_endpoint, dst_endpoint)).model_dump()
    )
    user_input_dict["optical_path"] = user_input_dict["optical_path"].split(";")
    return user_input_dict


def modify_optical_spectrum_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalSpectrumServiceSubscription,
    block_field_name: str = "optical_spectrum_service",
) -> FormGenerator:
    """Generate the initial input form for modifying an Optical Spectrum subscription.

    The form is prefilled with the current values of the subscription, so
    unchanged fields remain intact. It is a thin composition of the customer
    page, the shipped page sequence (:func:`modify_optical_spectrum_form_pages`)
    and the summary form.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical
            Spectrum product. Consumers that compose the shipped block under a
            different attribute name pass their own model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Optical Spectrum block.
    """
    subscription = subscription_model.from_subscription(subscription_id)
    user_input_dict = yield from customer_choice_form_page(include=subscription.customer_id)
    user_input_dict.update((yield from modify_optical_spectrum_form_pages(subscription, block_field_name)))

    block = getattr(subscription, block_field_name)
    summary_fields = ["customer_id", "optical_spectrum_name", "frequency_min", "frequency_max"]
    yield from modify_summary_form(
        user_input_dict,
        block,
        summary_fields,
        extra_before={"customer_id": subscription.customer_id},
    )

    return user_input_dict | {"subscription": subscription}


@step("Updating Optical Spectrum block")
def update_optical_spectrum_block(
    optical_module_block: OpticalSpectrumServiceBlockProvisioning,
    optical_spectrum_name: str,
    frequency_min: Frequency,
    frequency_max: Frequency,
) -> State:
    """Update the Optical Spectrum block in the state from the modify-form keys.

    The spectrum name and passband are overwritten with the form values; the old
    passband is returned in the state so the following circuit modification step
    can compare it with the new one. The shipped modify block steps never persist
    a changed ``customer_id`` (the form still emits it; add your own step if your
    product tracks it). Workflow steps execute with the state serialized between
    steps, so the block is re-hydrated from its serialized form before it is
    updated.

    Args:
        optical_module_block: The Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY`` (the provisioning variant, while
            the subscription is being modified).
        optical_spectrum_name: The new name of the spectrum.
        frequency_min: The new start frequency of the passband.
        frequency_max: The new end frequency of the passband.
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    old_passband = block.optical_spectrum_passband
    old_section_ids = [str(section.subscription_instance_id) for section in block.optical_spectrum_sections]
    block.optical_spectrum_name = optical_spectrum_name
    block.optical_spectrum_passband = (frequency_min, frequency_max)
    return {
        OPTICAL_MODULE_BLOCK_STATE_KEY: block,
        "old_passband": old_passband,
        "old_section_ids": old_section_ids,
    }


@step("Dividing the optical path into single-platform sections")
def divide_path_into_sections(
    optical_module_block: OpticalSpectrumServiceBlockProvisioning,
    optical_path: list[UUIDstr],
) -> State:
    """Split the chosen optical path into single-platform sections.

    The source and destination add/drop port blocks are reused from the existing
    sections; the interior ports chosen by the form are loaded and the resulting
    sections are stored back into the block in the state.

    The replaced section instances are pruned by the subscription save at the end
    of the shipped modify workflow (``set_status(ACTIVE)``), not by this step:
    ``ProductBlockModel.save`` only writes the block tree and rewrites the
    ``depends_on`` relations, it does not delete instances that are no longer
    referenced. A failed modify therefore leaves the old section instances as
    unreachable orphan rows until the next successful subscription save; this is
    safe (they are no longer reachable through the block relations) but they are
    not visible in the domain model. The explicit save below is required because
    the new section blocks are not in the database yet and workflow steps execute
    with the state serialized between steps, which drops their in-memory
    ``db_model`` (mirrors the create workflow, where ``set_status`` persists the
    sections built by the construct step).

    Args:
        optical_module_block: The Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
        optical_path: The interior port subscription instance ids of the chosen path.
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    sections = block.optical_spectrum_sections
    src_port = sections[0].optical_spectrum_section_add_drop_ports[0]
    dst_port = sections[-1].optical_spectrum_section_add_drop_ports[-1]

    interior = [load_ols_port(port_id) for port_id in optical_path]
    new_sections = split_loaded_path_into_loaded_sections([src_port, *interior, dst_port])
    store_loaded_sections_into_spectrum_block(new_sections, block)

    # The new section blocks are not in the database yet and workflow steps execute with
    # the state serialized between steps, which drops their in-memory ``db_model``. Persist
    # them here, while the step still owns the in-memory instances, so the following steps
    # can re-hydrate them from the database (mirrors the create workflow, where
    # ``set_status`` persists the sections built by the construct step).
    block.save(subscription_id=block.owner_subscription_id, status=SubscriptionLifecycle.PROVISIONING)

    return {OPTICAL_MODULE_BLOCK_STATE_KEY: block}


def _section_port_sequence(section: OpticalSpectrumSectionBlockProvisioning) -> tuple[str, ...]:
    """Return the ordered port subscription instance ids of a section."""
    add_drop_ports = section.optical_spectrum_section_add_drop_ports
    return (
        str(add_drop_ports[0].subscription_instance_id),
        *(str(port.subscription_instance_id) for port in section.optical_spectrum_section_express_ports),
        str(add_drop_ports[-1].subscription_instance_id),
    )


def _sections_signature(sections: list[OpticalSpectrumSectionBlockProvisioning]) -> tuple[tuple[str, ...], ...]:
    """Return the port sequences of the sections, used to detect a path change."""
    return tuple(_section_port_sequence(section) for section in sections)


@step("Modifying optical spectrum sections")
def modify_optical_sections(
    optical_module_block: OpticalSpectrumServiceBlockProvisioning,
    old_passband: Passband,
    old_section_ids: list[UUIDstr],
) -> State:
    """Modify the optical circuit of every spectrum section on the devices.

    Operates only on the Optical Spectrum block found in the state under
    ``OPTICAL_MODULE_BLOCK_STATE_KEY``, the same block the rest of the shipped
    block steps act on. The circuits are converged by identity with the single
    idempotent optical-circuit primitive; the old passband is not needed to
    find them. The old section ids are still used to detect a path change.

    When the chosen path differs from the previous one, the OEL explicit route
    cannot be updated in place (ED-OEL has no ``EXPLICITROUTE``), so the old
    circuits are deleted and the new ones ensured. The old circuits are torn
    down by
    :func:`orchestrator.optical.workflows.optical_spectrum_service.shared.delete_optical_spectrum_sections`,
    which deletes each source node's OEL only after all of its OSNCs are gone and
    only when no other OSNC on the node still uses it (otherwise the OEL is left
    in place because other OSNCs still need it).

    Args:
        optical_module_block: The Optical Spectrum block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
        old_passband: The passband the circuits had before the modification.
        old_section_ids: Subscription instance ids of the sections before the
            modification, used to delete the old circuits when the path changed.
    """
    block = optical_spectrum_block_from_state(optical_module_block)
    passband = block.optical_spectrum_passband
    spectrum_name = block.optical_spectrum_name
    if spectrum_name is None:
        msg = "Optical spectrum name is not set"
        raise ValueError(msg)
    snapped = snap_passband_to_grid(passband, FLEXILS_SPECTRAL_GRID_MHZ)
    snapped_changed = tuple(snapped) != tuple(passband)
    if snapped_changed:
        logger.warning(
            "Snapping off-grid spectrum passband to the 12.5 GHz grid",
            expected_passband=list(passband),
            snapped_passband=list(snapped),
        )
        block.optical_spectrum_passband = snapped
        passband = snapped
    carrier_width = passband[1] - passband[0]
    central_frequency = int((passband[0] + passband[1]) / 2)
    carrier = (central_frequency, carrier_width)
    circuit_identifier = str(block.subscription_instance_id)

    old_sections = [load_spectrum_section(section_id) for section_id in old_section_ids]
    new_sections = list(block.optical_spectrum_sections)

    results: dict[str, Any] = {}
    if _sections_signature(old_sections) == _sections_signature(new_sections):
        for section in new_sections:
            src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
            results[src_node.management.optical_module_node_fqdn] = ensure_optical_circuit(
                src_node,
                section,
                optical_spectrum_name=spectrum_name,
                passband=passband,
                carrier=carrier,
                label=spectrum_name,
                circuit_identifier=circuit_identifier,
            )
        state: State = {"configuration_results": results}
        if snapped_changed:
            state[OPTICAL_MODULE_BLOCK_STATE_KEY] = block
        return state

    # The path changed: tear down the old circuits (OSNCs) and their now-unused
    # OELs, then ensure the new ones. The OEL teardown rule lives in the shared
    # helper: a node's OEL is deleted only when no other OSNC still references it.
    results.update(
        delete_optical_spectrum_sections(
            old_sections,
            old_passband,
            spectrum_name,
            circuit_identifier,
        )
    )

    for section in new_sections:
        src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
        results[src_node.management.optical_module_node_fqdn] = ensure_optical_circuit(
            src_node,
            section,
            spectrum_name,
            passband,
            carrier,
            label=spectrum_name,
            circuit_identifier=circuit_identifier,
        )

    state = {"configuration_results": results}
    if snapped_changed:
        state[OPTICAL_MODULE_BLOCK_STATE_KEY] = block
    return state


#: Modify steps operating on the Optical Spectrum block in the state. The block
#: is persisted by the last step, because workflow steps reload the subscription
#: from the database and would otherwise lose the mutations.
MODIFY_OPTICAL_SPECTRUM_BLOCK_STEPS: StepList = (
    begin
    >> update_optical_spectrum_block
    >> divide_path_into_sections
    >> modify_optical_sections
    >> refresh_optical_spectrum_used_passbands
    >> save_optical_module_block
)


@modify_workflow(initial_input_form=modify_optical_spectrum_form_generator)
def modify_optical_spectrum() -> StepList:
    """Workflow to modify an existing Optical Spectrum service subscription.

    The workflow is valid for the shipped :class:`OpticalSpectrum` product type
    only: it loads the block from the ``optical_spectrum_service`` attribute of
    the shipped subscription models. The source and destination add/drop port
    blocks are reused from the existing sections, so the form recomputes the path
    between the existing source and destination nodes. Consumers with their own
    product type compose their own modify workflow with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_spectrum_block
        >> MODIFY_OPTICAL_SPECTRUM_BLOCK_STEPS
        >> set_optical_spectrum_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "LINE_SYSTEM_ROLES",
    "MODIFY_OPTICAL_SPECTRUM_BLOCK_STEPS",
    "modify_optical_spectrum",
    "modify_optical_spectrum_form_generator",
    "modify_optical_spectrum_form_pages",
    "update_optical_spectrum_block",
]
