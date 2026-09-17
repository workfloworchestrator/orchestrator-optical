"""Create Optical Digital Service workflow.

This module ships the ready-to-use ``create_optical_digital_service`` workflow
for the shipped Optical Digital Service product type, together with the
importable parts: the FormPages of the create form (as the
:func:`create_optical_digital_service_form_pages` page sequence), the block
population logic and the step list that operates on the Optical Digital Service
block found in the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.

Consumers that keep the shipped product type register the shipped workflow;
consumers with their own model that has-a the shipped block compose their own
``@create_workflow`` with the parts. The shipped workflow itself is composed
from the shipped parts: the construct step builds the shipped subscription
model, creates or links the client port blocks (transponder client ports are
created, coherent pluggables are linked from their own subscriptions), links
or creates the transport channel blocks (with their spectra and sections) and transitions the subscription to
PROVISIONING, the shipped block steps configure the transponders, deploy the
optical circuits of the new channels, refresh the passbands in use and persist
the PROVISIONING block found in the state under
``OPTICAL_MODULE_BLOCK_STATE_KEY``, and the shipped description step finalizes
the subscription. The shipped form generator is a thin composition of the
shipped pages and the summary form, without hooks: consumers build their own
form generator by yielding from the shipped page sequence in one line and
adding their own pages::

    user_input_dict = yield from create_optical_digital_service_form_pages(product_name)
    user_input_dict.update((yield my_own_page).model_dump())
    yield from create_summary_form(user_input_dict, product_name, summary_fields)
"""

from time import sleep
from typing import Annotated, Any, cast
from uuid import uuid4

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice, choice_list
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.db import node_block_from_instance
from orchestrator.optical.hal.adapters.nokia_flexils.spectrum import FLEXILS_SPECTRAL_GRID_MHZ
from orchestrator.optical.products.product_blocks.optical_digital_service import (
    OpticalDigitalServiceBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_types.optical_digital_service import (
    OpticalDigitalServiceSubscriptionProvisioning,
)
from orchestrator.optical.utils.custom_types.frequencies import (
    Frequency,
    SpectralWidth,
    ensure_passband_aligned_to_grid,
    passband_from,
)
from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.block import save_optical_module_block
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_digital_service.shared import (
    DIRECT_CONNECTION,
    PROVISION_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS,
    ChannelReuseGroup,
    align_optical_digital_tx_power,
    build_optical_digital_service_block,
    ensure_circuit_label_token_valid,
    has_new_channels_with_sections,
    is_packet_node_host,
    line_port_selector,
    new_optical_digital_service_subscription,
    optical_digital_endpoint_selector,
    optical_digital_service_block_from_state,
    optical_digital_service_speed_and_type,
    optical_digital_service_speed_and_type_for_product,
    optical_transport_mode_selector,
    port_ids_used_by_digital_services,
    refresh_optical_digital_used_passbands,
    reject_placeholder_transport_mode,
    resolve_channels_by_names,
    set_optical_digital_service_subscription_description,
    unused_coherent_pluggable_selector,
    validate_line_port_mode,
)
from orchestrator.optical.workflows.optical_pipe.shared import multiple_optical_pipe_selector_of_types
from orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum_service import (
    create_optical_spectrum_constraints_form,
    create_optical_spectrum_waypoints_form,
)
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    LINE_SYSTEM_ROLES,
    NO_OPTICAL_PATH_FOUND_MSG,
    OPTICAL_PIPE_PRODUCT_TYPES,
    NoOpticalPathFoundError,
    all_shortest_paths_through_waypoints,
    are_trx_and_oadm_in_the_same_shelf_for_g30s_in_path,
    check_optical_spectrum_add_drop_port_availability,
    find_add_drop_ports,
    human_readable_transport_channel_path_selector,
    multiple_optical_node_selector,
)
from orchestrator.optical.workflows.shared import create_summary_form, optical_port_selector

logger = get_logger(__name__)


def _normalize_channel_names(channel_name_1: str, channel_name_2: str = "") -> list[str]:
    """Return the non-blank transport channel names, stripped, in order."""
    return [name.strip() for name in (channel_name_1, channel_name_2) if name.strip()]


def _decode_optical_path(value: str) -> list[UUIDstr]:
    """Split a ``";"``-joined optical-path Choice value into port instance ids."""
    return value.split(";")


def _no_optical_path_placeholder_choice() -> type[Choice]:
    """Return the rejecting placeholder path Choice offered when no optical path resolves."""
    return cast(
        type[Choice],
        Choice(
            NO_OPTICAL_PATH_FOUND_MSG,
            [(NO_OPTICAL_PATH_FOUND_MSG, NO_OPTICAL_PATH_FOUND_MSG)],
        ),
    )


def normalize_channel_names(channel_name_1: str, channel_name_2: str = "") -> list[str]:
    """Return the non-blank transport channel names, stripped, in order (public alias)."""
    return _normalize_channel_names(channel_name_1, channel_name_2)


def decode_optical_path(value: str) -> list[UUIDstr]:
    """Split a ``";"``-joined optical-path Choice value into port instance ids (public alias)."""
    return _decode_optical_path(value)


def no_optical_path_placeholder_choice() -> type[Choice]:
    """Return the rejecting placeholder path Choice (public alias)."""
    return _no_optical_path_placeholder_choice()


#: Seconds to wait for the lasers and the line system to settle before power alignment.
SETTLE_BEFORE_POWER_ALIGNMENT_S = 30

#: Summary fields always shown by the Optical Digital Service create summary form.
SUMMARY_FIELDS_BASE = [
    "customer_id",
    "optical_digital_service_name",
    "src_node_block_instance_id",
    "dst_node_block_instance_id",
    "channel_name_1",
    "unused_src_client",
    "unused_dst_client",
]

#: Additional summary fields for the new-transport-channels branch.
SUMMARY_FIELDS_NEW = [
    "src_lines",
    "dst_lines",
    "optical_transport_mode",
    "frequency_1",
    "bandwidth_1",
    "intermediate_node_instance_ids",
    "exclude_node_instance_ids",
    "exclude_pipe_instance_ids",
    "optical_path",
]

#: Additional summary fields for reverse-multiplexed (dual-channel) services.
SUMMARY_FIELDS_DUAL_EXTRA = ["frequency_2", "bandwidth_2"]


def _summary_fields_for_create(user_input_dict: dict) -> list[str]:
    """Return the summary fields for the create summary form (reuse vs new, single vs dual)."""
    summary_fields = list(SUMMARY_FIELDS_BASE)
    if user_input_dict.get("channel_name_2"):
        summary_fields.append("channel_name_2")
    if "reuse_channel_ids" in user_input_dict:
        summary_fields.append("reuse_channel_ids")
    else:
        summary_fields += SUMMARY_FIELDS_NEW
        if user_input_dict.get("channel_name_2"):
            summary_fields += SUMMARY_FIELDS_DUAL_EXTRA
    return summary_fields


def create_optical_digital_service_identity_form(product_name: str) -> type[FormPage]:
    """Return the identity FormPage of the Optical Digital Service create form.

    This is the first page of the shipped create form: the user-facing service
    name, the two endpoint hosts (validated different) and the names of the
    transport channels (one, or two for reverse multiplexing). The channel
    names ARE the new-vs-reuse fork: names that match already provisioned
    channels reuse them (spare capacity and terminations checked here and
    re-checked by the construct step), new names are created by the later
    pages. Speed and framing type are NOT asked and NOT carried in the form:
    they are fixed inputs stored 1:1 on the product row.

    Args:
        product_name: Name of the product being created, used as the page title.

    Returns:
        The identity FormPage of the shipped create form.
    """
    src_node_choice = optical_digital_endpoint_selector("This service starts on this endpoint host: ")
    dst_node_choice = optical_digital_endpoint_selector("...and ends on this endpoint host: ")

    class CreateOpticalDigitalServiceIdentityForm(FormPage):
        model_config = ConfigDict(title=product_name)

        optical_digital_service_name: str
        src_node_block_instance_id: src_node_choice
        dst_node_block_instance_id: dst_node_choice
        channel_name_1: str
        channel_name_2: Annotated[
            str,
            Field(
                title="Second transport channel",
                description=(
                    "Name of the second transport channel when this service is carried over "
                    "2 channels (reverse multiplexing); leave empty for a single-channel service."
                ),
            ),
        ] = ""

        @model_validator(mode="after")
        def validate_endpoints(self) -> "CreateOpticalDigitalServiceIdentityForm":
            if self.src_node_block_instance_id == self.dst_node_block_instance_id:
                msg = "The source and destination endpoint hosts must be different"
                raise ValueError(msg)
            if not self.channel_name_1.strip():
                msg = "The first transport channel name cannot be blank"
                raise ValueError(msg)
            ensure_circuit_label_token_valid(self.optical_digital_service_name, "digital service")
            names = _normalize_channel_names(self.channel_name_1, self.channel_name_2)
            for name in names:
                ensure_circuit_label_token_valid(name, "transport channel")
            speed, _service_type = optical_digital_service_speed_and_type_for_product(product_name)
            # Early hint only: the page sequence re-resolves to branch the form and the
            # construct step re-resolves authoritatively, so a stale result here is harmless.
            resolve_channels_by_names(names, speed, self.src_node_block_instance_id, self.dst_node_block_instance_id)
            return self

    return CreateOpticalDigitalServiceIdentityForm


def create_optical_digital_service_client_ports_form(
    product_name: str,
    src_host_id: UUIDstr,
    dst_host_id: UUIDstr,
) -> type[FormPage]:
    """Return the client ports FormPage of the Optical Digital Service create form.

    This is the second page of the shipped create form: the client port of both
    endpoint hosts. On a packet node the coherent pluggable is selected among
    the existing pluggable blocks hosted on the node that are not already in
    use by another digital service; on a transponder host the client port is
    selected among the device client ports not already in use (the device must
    be reachable, otherwise the page fails). In both cases the value is a
    string: an instance id or a port name.

    Args:
        product_name: Name of the product being created, used as the page title.
        src_host_id: Subscription instance id of the source endpoint host block.
        dst_host_id: Subscription instance id of the destination endpoint host block.

    Returns:
        The client ports FormPage of the shipped create form.
    """

    def _client_field(host_id: UUIDstr, prompt: str) -> Any:
        if is_packet_node_host(host_id):
            return unused_coherent_pluggable_selector(host_id, prompt)
        return optical_port_selector(
            node_block_from_instance(host_id),
            roles=[OpticalPortRole.TRANSPONDER_CLIENT],
            prompt=prompt,
        )

    src_port_field: Any = _client_field(src_host_id, "Select the source client port")
    dst_port_field: Any = _client_field(dst_host_id, "Select the destination client port")

    class CreateOpticalDigitalServiceClientPortsForm(FormPage):
        model_config = ConfigDict(title=product_name)

        unused_src_client: src_port_field
        unused_dst_client: dst_port_field

        @model_validator(mode="after")
        def validate_client_ports(self) -> "CreateOpticalDigitalServiceClientPortsForm":
            for host_id, port_ref in (
                (src_host_id, self.unused_src_client),
                (dst_host_id, self.unused_dst_client),
            ):
                if is_packet_node_host(host_id):
                    if str(port_ref) in port_ids_used_by_digital_services():
                        msg = "This coherent pluggable is already in use by another digital service"
                        raise ValueError(msg)
                else:
                    check_optical_spectrum_add_drop_port_availability(node_block_from_instance(host_id), str(port_ref))
            return self

    return CreateOpticalDigitalServiceClientPortsForm


def create_optical_digital_service_lines_form(
    product_name: str,
    num_channels: int,
    src_line_choice: type[Choice],
    dst_line_choice: type[Choice],
) -> type[FormPage]:
    """Return the lines FormPage of the Optical Digital Service create form.

    This page is only shown for new transport channels: each side picks one
    line port (two when reverse-multiplexed) among the choices computed for
    the endpoint host's card — the patched, unused line ports on the same
    card as the client on a transponder host, the client pluggable itself
    (single option) on a packet node (see :func:`line_port_selector
    <orchestrator.optical.workflows.optical_digital_service.shared.line_port_selector>`).
    The validator re-checks availability like any other selection.

    Args:
        product_name: Name of the product being created, used as the page title.
        num_channels: Number of new transport channels (1, or 2 for reverse multiplexing).
        src_line_choice: ``Choice`` of the source line ports.
        dst_line_choice: ``Choice`` of the destination line ports.

    Returns:
        The lines FormPage of the shipped create form.
    """
    src_lines_type = choice_list(src_line_choice, min_items=num_channels, max_items=num_channels, unique_items=True)
    dst_lines_type = choice_list(dst_line_choice, min_items=num_channels, max_items=num_channels, unique_items=True)

    class CreateOpticalDigitalServiceLinesForm(FormPage):
        model_config = ConfigDict(title=product_name)

        src_lines: src_lines_type
        dst_lines: dst_lines_type

        @model_validator(mode="after")
        def validate_lines(self) -> "CreateOpticalDigitalServiceLinesForm":
            for line_id in [*self.src_lines, *self.dst_lines]:
                if str(line_id) in port_ids_used_by_digital_services():
                    msg = "This line port is already in use by another digital service"
                    raise ValueError(msg)
            return self

    return CreateOpticalDigitalServiceLinesForm


def create_optical_digital_service_channels_form(
    product_name: str,
    num_channels: int,
    mode_choice: type[Choice],
) -> type[FormPage]:
    """Return the transport channels FormPage of the Optical Digital Service create form.

    This page collects the shared operating mode and the central frequency
    and spectral width of each new transport channel (one, or two for reverse
    multiplexing). It is only shown for new transport channels: the names were
    already collected on the identity page. The mode is a drop-down over the
    intersection of the live mode tables of the selected line port cards (see
    :func:`optical_transport_mode_selector
    <orchestrator.optical.workflows.optical_digital_service.shared.optical_transport_mode_selector>`);
    when the cards share no common mode the drop-down holds only a rejecting
    placeholder. The authoritative check against the live modes of the line port
    cards re-runs in the construct step (see :func:`validate_line_port_mode
    <orchestrator.optical.workflows.optical_digital_service.shared.validate_line_port_mode>`).

    Args:
        product_name: Name of the product being created, used as the page title.
        num_channels: Number of new transport channels (1, or 2 for reverse multiplexing).
        mode_choice: ``Choice`` of the operating modes supported by the selected
            line ports.

    Returns:
        The transport channels FormPage of the shipped create form.
    """

    class CreateOpticalDigitalServiceChannelsForm(FormPage):
        model_config = ConfigDict(title=product_name)

        optical_transport_mode: mode_choice
        frequency_1: Frequency
        bandwidth_1: SpectralWidth

        @model_validator(mode="after")
        def validate_channels(self) -> "CreateOpticalDigitalServiceChannelsForm":
            reject_placeholder_transport_mode(str(self.optical_transport_mode))
            ensure_passband_aligned_to_grid(
                passband_from(self.frequency_1, self.bandwidth_1), FLEXILS_SPECTRAL_GRID_MHZ
            )
            return self

    if num_channels == 1:
        return CreateOpticalDigitalServiceChannelsForm

    class CreateOpticalDigitalServiceDualChannelsForm(CreateOpticalDigitalServiceChannelsForm):
        frequency_2: Frequency
        bandwidth_2: SpectralWidth

        @model_validator(mode="after")
        def validate_second_channel(self) -> "CreateOpticalDigitalServiceDualChannelsForm":
            ensure_passband_aligned_to_grid(
                passband_from(self.frequency_2, self.bandwidth_2), FLEXILS_SPECTRAL_GRID_MHZ
            )
            return self

    return CreateOpticalDigitalServiceDualChannelsForm


def create_optical_digital_service_path_form(path_choice: type[Choice]) -> type[FormPage]:
    """Return the path FormPage of the Optical Digital Service create form.

    This is the last page of the shipped create form (new channels only): the
    optical path of the first transport channel, chosen among the ones computed
    by the path engine. The page rejects the placeholder option used when no
    path was found. The ``"direct_connection"`` option is valid: it means the
    endpoints are directly connected with no line system in between.

    Unlike the spectrum path page, the chosen path is NOT validated for
    single-platform splittability here: digital sections are stored with the
    lenient vendor-grouping
    (:func:`orchestrator.optical.workflows.optical_spectrum_service.shared.store_list_of_ports_into_spectrum_sections`)
    rather than the strict single-platform split, so a strict check could
    reject paths that provision fine — and ``"direct_connection"`` carries no
    sections at all.

    Args:
        path_choice: The ``Choice`` selector of the available optical paths.

    Returns:
        The path FormPage of the shipped create form.
    """

    class CreateOpticalDigitalServicePathForm(FormPage):
        model_config = ConfigDict(title="Optical Path")

        optical_path: path_choice

        @model_validator(mode="after")
        def validate_data(self) -> "CreateOpticalDigitalServicePathForm":
            if self.optical_path == NO_OPTICAL_PATH_FOUND_MSG:
                msg = (
                    "No optical path found, please adjust the routing constraints "
                    "in the previous step or update fibers in the path."
                )
                raise ValueError(msg)
            return self

    return CreateOpticalDigitalServicePathForm


def optical_digital_service_path_choice(
    line_a_1: UUIDstr,
    line_b_1: UUIDstr,
    waypoint_node_instance_ids: list[UUIDstr] | None,
    passband: tuple[int, int],
    exclude_node_instance_ids: list[UUIDstr] | None,
    exclude_pipe_instance_ids: list[UUIDstr] | None,
) -> type[Choice]:
    """Create the optical-path selector between two transponder line ports.

    This mirrors :func:`orchestrator.optical.workflows.optical_spectrum_service.shared.transport_channel_path_selector`
    with ordered waypoints: the line ports resolve to their add/drop ports
    (or to themselves when directly connected), the waypoint engine computes
    the OLS interior, and each path is wrapped with the add/drop ends — the
    exact shape the trx engine produces, so :func:`build_optical_digital_service_block`
    consumes it unchanged. Every node reference is a block subscription instance id;
    subscription ids are never accepted here.

    Args:
        line_a_1: Subscription instance id of the first source line port block.
        line_b_1: Subscription instance id of the first destination line port block.
        waypoint_node_instance_ids: Ordered subscription instance ids of the intermediate
            Optical Node blocks the path must traverse.
        passband: The passband configuration for the optical path.
        exclude_node_instance_ids: Subscription instance ids of Optical Node blocks to exclude.
        exclude_pipe_instance_ids: Subscription instance ids of pipe blocks to exclude.

    Returns:
        A ``Choice`` class whose values are ``";"``-joined port instance ids.

    Raises:
        NoOpticalPathFoundError: If no valid path exists.
        ValueError: If waypoints are given for directly connected endpoints.
    """
    prompt = (
        "Select the optical path, if you don't see the desired path,"
        " adjust constraints in previous step or validate fibers along the path."
    )
    first_add_drop, last_add_drop = find_add_drop_ports(line_a_1, line_b_1)
    if (
        str(first_add_drop.subscription_instance_id) == line_b_1
        and str(last_add_drop.subscription_instance_id) == line_a_1
    ):
        if waypoint_node_instance_ids:
            msg = "The endpoints are directly connected: clear the intermediate nodes to proceed"
            raise ValueError(msg)
        return human_readable_transport_channel_path_selector([[]], prompt)
    src_ols_dev_id = str(first_add_drop.optical_port_host_node.subscription_instance_id)
    dst_ols_dev_id = str(last_add_drop.optical_port_host_node.subscription_instance_id)
    logger.debug(
        "Computing digital service optical path",
        src_line_id=str(line_a_1),
        dst_line_id=str(line_b_1),
        first_add_drop_id=str(first_add_drop.subscription_instance_id),
        last_add_drop_id=str(last_add_drop.subscription_instance_id),
        src_ols_dev_id=src_ols_dev_id,
        dst_ols_dev_id=dst_ols_dev_id,
        passband=passband,
    )
    ols_paths = all_shortest_paths_through_waypoints(
        src_ols_dev_id,
        dst_ols_dev_id,
        waypoint_node_instance_ids,
        passband,
        exclude_node_instance_ids,
        exclude_pipe_instance_ids,
    )
    wrapped_paths = []
    for path in ols_paths:
        wrapped = [str(first_add_drop.subscription_instance_id), *path, str(last_add_drop.subscription_instance_id)]
        if are_trx_and_oadm_in_the_same_shelf_for_g30s_in_path(wrapped):
            wrapped_paths.append(wrapped)
    if not wrapped_paths:
        if ols_paths:
            logger.warning(
                "All candidate optical paths were discarded by the G30 same-shelf filter",
                num_candidates=len(ols_paths),
            )
        raise NoOpticalPathFoundError(src=line_a_1, dst=line_b_1)
    return human_readable_transport_channel_path_selector(wrapped_paths, prompt)


def create_optical_digital_service_form_pages(product_name: str) -> FormGenerator:
    """Yield the FormPages of the Optical Digital Service create form, in order.

    This is the shipped create form as a page sequence: it yields the identity
    page (name, endpoints and transport channel names — the names ARE the
    new-vs-reuse fork), the client ports page, and then, only for new
    transport channels, the lines page, the channels page (mode,
    frequencies), the waypoints page, the constraints page and the path page.
    It returns the collected user input as a flat dict of the state keys,
    consumed by the shipped construct step
    (:func:`construct_optical_digital_service_subscription`). The customer of
    the subscription is collected separately by the consumer (see
    :func:`orchestrator.optical.workflows.customer.customer_choice_form_page`).

    Args:
        product_name: Name of the product being created.

    Returns:
        The collected user input of the shipped pages.
    """
    user_input_dict: dict[str, Any] = {}
    user_input_dict.update((yield create_optical_digital_service_identity_form(product_name)).model_dump())
    src_host_id = user_input_dict["src_node_block_instance_id"]
    dst_host_id = user_input_dict["dst_node_block_instance_id"]
    channel_names = _normalize_channel_names(user_input_dict["channel_name_1"], user_input_dict["channel_name_2"])
    user_input_dict["channel_name_1"] = channel_names[0]
    user_input_dict["channel_name_2"] = channel_names[1] if len(channel_names) > 1 else ""
    num_channels = len(channel_names)

    user_input_dict.update(
        (yield create_optical_digital_service_client_ports_form(product_name, src_host_id, dst_host_id)).model_dump()
    )
    speed, _service_type = optical_digital_service_speed_and_type_for_product(product_name)

    # Branch decision for the remaining pages. The construct step re-resolves
    # authoritatively: ``reuse_channel_ids`` below is summary display only.
    fork, group = resolve_channels_by_names(channel_names, speed, src_host_id, dst_host_id)
    if fork == "reuse":
        user_input_dict["reuse_channel_ids"] = ";".join(group.channel_ids) if group is not None else ""
        return user_input_dict

    user_input_dict.update(
        (
            yield from _yield_line_ports_pages(
                product_name,
                num_channels,
                src_host_id,
                dst_host_id,
                user_input_dict["unused_src_client"],
                user_input_dict["unused_dst_client"],
            )
        )
    )

    src_line_ids = [cast(UUIDstr, line_id) for line_id in user_input_dict["src_lines"]]
    dst_line_ids = [cast(UUIDstr, line_id) for line_id in user_input_dict["dst_lines"]]
    user_input_dict.update(
        (yield from _yield_new_channel_spec_pages(product_name, num_channels, src_line_ids, dst_line_ids))
    )
    return user_input_dict


def _yield_line_ports_pages(
    product_name: str,
    num_channels: int,
    src_host_id: UUIDstr,
    dst_host_id: UUIDstr,
    src_client: UUIDstr,
    dst_client: UUIDstr,
) -> FormGenerator:
    """Yield the lines page of the Optical Digital Service create form.

    Only shown for new transport channels: each side picks its line ports
    among the choices computed for the endpoint host's card. Returns the
    collected input (``src_lines``/``dst_lines``); the caller merges it.

    Args:
        product_name: Name of the product being created.
        num_channels: Number of new transport channels (1, or 2 for reverse multiplexing).
        src_host_id: Subscription instance id of the source endpoint host block.
        dst_host_id: Subscription instance id of the destination endpoint host block.
        src_client: The selected source client port (name or pluggable instance id).
        dst_client: The selected destination client port (name or pluggable instance id).

    Returns:
        The collected user input of the lines page.
    """
    src_line_choice = line_port_selector(src_host_id, src_client, "Select the source line ports")
    dst_line_choice = line_port_selector(dst_host_id, dst_client, "Select the destination line ports")
    user_input = yield create_optical_digital_service_lines_form(
        product_name, num_channels, src_line_choice, dst_line_choice
    )
    return user_input.model_dump()


def _yield_routing_constraint_pages(product_name: str) -> FormGenerator:
    """Yield the waypoints and constraints pages shared with the spectrum create form.

    Returns the collected input (``intermediate_node_instance_ids``,
    ``exclude_node_instance_ids``, ``exclude_pipe_instance_ids``); the caller merges it.

    Args:
        product_name: Name of the product being created.

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
    exclude_spans_choice = multiple_optical_pipe_selector_of_types(
        OPTICAL_PIPE_PRODUCT_TYPES,
        prompt="Do *not* pass through these Optical Pipes",
    )
    collected.update(
        (
            yield create_optical_spectrum_constraints_form(product_name, exclude_nodes_choice, exclude_spans_choice)
        ).model_dump()
    )
    return collected


def _yield_new_channel_spec_pages(
    product_name: str,
    num_channels: int,
    src_line_ids: list[UUIDstr],
    dst_line_ids: list[UUIDstr],
) -> FormGenerator:
    """Yield the new-channel spec pages of the Optical Digital Service create form.

    Only shown for new transport channels: the channels page (mode,
    frequencies), the waypoints page, the constraints page and the path page.
    Returns the collected input; the caller merges it.

    Args:
        product_name: Name of the product being created.
        num_channels: Number of new transport channels (1, or 2 for reverse multiplexing).
        src_line_ids: Subscription instance ids of the selected source line ports.
        dst_line_ids: Subscription instance ids of the selected destination line ports.

    Returns:
        The collected user input of the new-channel spec pages.
    """
    collected: dict[str, Any] = {}
    mode_choice = optical_transport_mode_selector([*src_line_ids, *dst_line_ids])
    collected.update(
        (yield create_optical_digital_service_channels_form(product_name, num_channels, mode_choice)).model_dump()
    )
    collected.update((yield from _yield_routing_constraint_pages(product_name)))

    passband = passband_from(collected["frequency_1"], collected["bandwidth_1"])
    try:
        path_choice = optical_digital_service_path_choice(
            src_line_ids[0],
            dst_line_ids[0],
            collected["intermediate_node_instance_ids"],
            passband,
            collected["exclude_node_instance_ids"],
            collected["exclude_pipe_instance_ids"],
        )
    except (NoOpticalPathFoundError, ValueError):
        # No path (or an unresolvable fiber attachment, e.g. a coherent
        # pluggable whose fiber attachment cannot be resolved yet): the form
        # offers the rejecting placeholder so the user adjusts the constraints.
        logger.exception(
            "No optical path found",
            src_lines=src_line_ids,
            dst_lines=dst_line_ids,
            passband=passband,
        )
        path_choice = _no_optical_path_placeholder_choice()

    collected.update((yield create_optical_digital_service_path_form(path_choice)).model_dump())
    collected["optical_path"] = _decode_optical_path(collected["optical_path"])
    return collected


def create_optical_digital_service_form_generator(product_name: str) -> FormGenerator:
    """Generate the initial input form for creating an Optical Digital Service.

    The form emits the flat ``optical_*`` state keys consumed by the shipped
    construct step (:func:`construct_optical_digital_service_subscription`). It is a
    thin composition of the customer page, the shipped page sequence
    (:func:`create_optical_digital_service_form_pages`) and the summary form.

    Args:
        product_name: Name of the product being created.
    """
    user_input_dict = yield from customer_choice_form_page(title=product_name)
    user_input_dict.update((yield from create_optical_digital_service_form_pages(product_name)))

    yield from create_summary_form(user_input_dict, product_name, _summary_fields_for_create(user_input_dict))

    return user_input_dict


def _reuse_channel_plan(
    group: ChannelReuseGroup | None,
) -> tuple[list[UUIDstr], list[str], list[UUIDstr], list[UUIDstr], list[Frequency], list[SpectralWidth]]:
    """Return the build args for the reuse branch (links the group, ignores new-channel inputs)."""
    if group is None:
        msg = "Could not resolve the named transport channels to a reusable channel group"
        raise ValueError(msg)
    return (list(group.channel_ids), [], [], [], [], [])


def _new_channel_plan(
    channel_names: list[str],
    src_lines: list[UUIDstr] | None,
    dst_lines: list[UUIDstr] | None,
    optical_transport_mode: str | None,
    frequency_1: Frequency | None,
    bandwidth_1: SpectralWidth | None,
    frequency_2: Frequency | None,
    bandwidth_2: SpectralWidth | None,
) -> tuple[list[UUIDstr], list[str], list[UUIDstr], list[UUIDstr], list[Frequency], list[SpectralWidth]]:
    """Return the build args for the new-channels branch (validates lines, freqs and live card modes)."""
    if src_lines is None or dst_lines is None:
        msg = "New transport channels require selected line ports"
        raise ValueError(msg)
    if len(src_lines) != len(channel_names) or len(dst_lines) != len(channel_names):
        msg = "The line selection must hold one port per side per transport channel"
        raise ValueError(msg)
    if frequency_1 is None or bandwidth_1 is None:
        msg = "New transport channels require frequencies and bandwidths"
        raise ValueError(msg)
    if optical_transport_mode is None:
        msg = "New transport channels require an operating mode"
        raise ValueError(msg)
    line_ids_a = list(src_lines)
    line_ids_b = list(dst_lines)
    for line_id, side in (
        *[(line_id, "source") for line_id in line_ids_a],
        *[(line_id, "destination") for line_id in line_ids_b],
    ):
        validate_line_port_mode(line_id, optical_transport_mode, side)
    frequencies = [frequency_1]
    bandwidths = [bandwidth_1]
    if len(channel_names) == 2:  # noqa: PLR2004
        if frequency_2 is None or bandwidth_2 is None:
            msg = "The second transport channel requires its frequency and bandwidth"
            raise ValueError(msg)
        frequencies.append(frequency_2)
        bandwidths.append(bandwidth_2)
    return ([], list(channel_names), line_ids_a, line_ids_b, frequencies, bandwidths)


@step("Construct Optical Digital Service Subscription")
def construct_optical_digital_service_subscription(
    product: UUIDstr,
    customer_id: UUIDstr,
    optical_digital_service_name: str,
    src_node_block_instance_id: UUIDstr,
    dst_node_block_instance_id: UUIDstr,
    unused_src_client: UUIDstr,
    unused_dst_client: UUIDstr,
    channel_name_1: str,
    channel_name_2: str = "",
    src_lines: list[UUIDstr] | None = None,
    dst_lines: list[UUIDstr] | None = None,
    optical_transport_mode: str | None = None,
    frequency_1: Frequency | None = None,
    bandwidth_1: SpectralWidth | None = None,
    frequency_2: Frequency | None = None,
    bandwidth_2: SpectralWidth | None = None,
    optical_path: list[UUIDstr] | None = None,
) -> State:
    """Construct the PROVISIONING domain subscription model for an Optical Digital Service.

    Builds the shipped ``OpticalDigitalService`` model around
    :func:`orchestrator.optical.workflows.optical_digital_service.shared.build_optical_digital_service_block`
    (the anti-corruption point: consumers with their own model write their own
    construct step instead) and transitions it to PROVISIONING in memory, so the
    block under ``OPTICAL_MODULE_BLOCK_STATE_KEY`` meets the contract of
    :func:`orchestrator.optical.workflows.block.save_optical_module_block`.
    """
    subscription_id = uuid4()
    optical_digital_service_speed, optical_digital_service_type = optical_digital_service_speed_and_type(product)
    channel_names = _normalize_channel_names(channel_name_1, channel_name_2)
    # Authoritative fork: re-resolved here because the database may have changed since the
    # form was filled in. The form's ``reuse_channel_ids`` (summary display only) is ignored.
    fork, group = resolve_channels_by_names(
        channel_names, optical_digital_service_speed, src_node_block_instance_id, dst_node_block_instance_id
    )
    if fork == "reuse":
        reuse_ids, channel_names, line_ids_a, line_ids_b, frequencies, bandwidths = _reuse_channel_plan(group)
    else:
        reuse_ids, channel_names, line_ids_a, line_ids_b, frequencies, bandwidths = _new_channel_plan(
            channel_names,
            src_lines,
            dst_lines,
            optical_transport_mode,
            frequency_1,
            bandwidth_1,
            frequency_2,
            bandwidth_2,
        )
    digital_block = build_optical_digital_service_block(
        subscription_id=subscription_id,
        optical_digital_service_name=optical_digital_service_name,
        optical_digital_service_speed=optical_digital_service_speed,
        optical_digital_service_type=optical_digital_service_type,
        src_host_id=src_node_block_instance_id,
        dst_host_id=dst_node_block_instance_id,
        src_client_port=unused_src_client,
        dst_client_port=unused_dst_client,
        reuse_channel_ids=reuse_ids,
        channel_names=channel_names,
        line_port_ids_a=line_ids_a,
        line_port_ids_b=line_ids_b,
        frequencies=frequencies,
        bandwidths=bandwidths,
        optical_transport_mode=optical_transport_mode or "",
        optical_path=optical_path or [DIRECT_CONNECTION],
    )
    subscription = new_optical_digital_service_subscription(
        product,
        str(customer_id),
        digital_block,
        optical_digital_service_speed,
        optical_digital_service_type,
    )
    subscription = OpticalDigitalServiceSubscriptionProvisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        OPTICAL_MODULE_BLOCK_STATE_KEY: subscription.optical_digital_service,
    }


@step("Waiting for the transponders and ROADMs to settle")
def wait_before_power_alignment(optical_module_block: OpticalDigitalServiceBlockInactive) -> State:
    """Wait for the lasers and the line system to settle before measuring power.

    The step sleeps only when the block holds new transport channels with
    deployed sections; reused-only services skip the wait.

    Args:
        optical_module_block: The Optical Digital Service block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
    """
    block = optical_digital_service_block_from_state(optical_module_block)
    if has_new_channels_with_sections(block):
        sleep(SETTLE_BEFORE_POWER_ALIGNMENT_S)
    return {}


#: Create steps operating on the Optical Digital Service block in the state. Every step
#: is block-level: the shared provisioning push (line/client/cross-connect
#: configuration and optical-circuit ensure of every channel, see
#: ``PROVISION_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS``) runs first, then the
#: passbands in use are refreshed, the transmit power is aligned and the block is
#: persisted by the last step, because workflow steps execute with the state
#: serialized between steps (the block is re-hydrated from its serialized form
#: before every step operates on it). The block is assumed to be in the PROVISIONING
#: lifecycle status with its mandatory fields and channels already set: the caller's
#: construct step provides it (see :func:`construct_optical_digital_service_subscription`).
#: Consumers with their own model run this list after constructing their
#: subscription the same way and putting their block in the state under
#: ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
CREATE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS: StepList = StepList(
    [
        *PROVISION_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS,
        refresh_optical_digital_used_passbands,
        wait_before_power_alignment,
        align_optical_digital_tx_power,
        save_optical_module_block,
    ]
)


@create_workflow(initial_input_form=create_optical_digital_service_form_generator)
def create_optical_digital_service() -> StepList:
    """Workflow to create a new Optical Digital Service subscription.

    The workflow is composed from the shipped parts: the construct step builds
    the shipped :class:`OpticalDigitalService` model, creates the client port
    blocks, links or creates the transport channels and transitions the
    subscription to PROVISIONING, the shipped block steps configure the devices
    and persist the block, and the shipped description step finalizes the
    subscription. It is therefore only valid for the shipped product type;
    consumers with their own product type compose their own create workflow
    with the same parts.
    """
    return (
        begin
        >> construct_optical_digital_service_subscription
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> CREATE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS
        >> set_optical_digital_service_subscription_description
        >> store_process_subscription()
    )


__all__ = [
    "CREATE_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS",
    "SETTLE_BEFORE_POWER_ALIGNMENT_S",
    "SUMMARY_FIELDS_BASE",
    "SUMMARY_FIELDS_DUAL_EXTRA",
    "SUMMARY_FIELDS_NEW",
    "construct_optical_digital_service_subscription",
    "create_optical_digital_service",
    "create_optical_digital_service_channels_form",
    "create_optical_digital_service_client_ports_form",
    "create_optical_digital_service_form_generator",
    "create_optical_digital_service_form_pages",
    "create_optical_digital_service_identity_form",
    "create_optical_digital_service_lines_form",
    "create_optical_digital_service_path_form",
    "decode_optical_path",
    "no_optical_path_placeholder_choice",
    "normalize_channel_names",
    "optical_digital_service_path_choice",
    "wait_before_power_alignment",
]
