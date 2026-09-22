"""Bulk creation of Optical Pipes from CSV data.

This module ships the ``bulk_create_optical_pipes`` system task: the operator
pastes a CSV payload, the task validates it and launches one shipped Optical
Pipe create sub-workflow per row (``create_fiber_span``,
``create_fiber_patch`` or ``create_leased_spectrum``, selected from the row's
pipe type). Sub-workflow progress is tracked in the Subscriptions page, like
any other workflow.

The CSV has one row per pipe with exactly these headers::

    pipe_type,node_a_fqdn,port_a_name,node_b_fqdn,port_b_name,optical_pipe_name,provider_name

* ``pipe_type``: ``Span``, ``Patch`` or ``Leased Spectrum``; selects the
  sub-workflow.
* ``node_a_fqdn``/``node_b_fqdn``: FQDNs of the ACTIVE nodes hosting the ends.
* ``port_a_name``/``port_b_name``: device-native port names on the nodes.
* ``optical_pipe_name``: pipe identifier (may be empty: it defaults to
  ``"<fqdn A> <port A> --- <fqdn B> <port B>"``).
* ``provider_name``: third-party provider name; mandatory on leased spectrum
  rows (it is prefixed to the pipe name by the sub-workflow), forbidden
  otherwise.

Validation runs in two layers: the form checks the confirmation, the headers
and the per-row formats (plus endpoint reuse within the CSV); the resolve step
re-checks against the database (node lookup, span same-vendor rule, ports not
already in use). Whether a port exists on its device with a role the pipe type
supports is validated by each sub-workflow when it renders its termination
form from the device, so the bulk task performs no device calls itself.

This task is the generalized port of the ``bulk_create_optical_fibers`` task
of the legacy implementation: the GARR-specific columns (``garrxdb_id``) and
the fields the new pipe blocks no longer carry (``total_loss``,
``fiber_types``, ``lengths``) are gone, and the FQDN-prefix port regexes are
replaced by the database port-usage check plus the sub-workflow device
enumeration.
"""

from time import sleep
from typing import Annotated, Any, TypedDict, cast

from pydantic import Field, TypeAdapter, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.db import db
from orchestrator.core.forms import FormPage
from orchestrator.core.services.processes import start_process
from orchestrator.core.services.products import get_product_by_name
from orchestrator.core.targets import Target
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, done, step, workflow
from orchestrator.optical.db import (
    node_block_from_instance,
    node_instance_id_of_subscription,
    subscription_instances_by_block_type_and_resource_value,
)
from orchestrator.optical.products import ProductName
from orchestrator.optical.products.product_blocks.optical_node_management import (
    OpticalModuleNodeManagementBlock,
)
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import OpticalPipeType
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_pipe.shared import SPAN_NODE_ROLES, default_pipe_identifier
from orchestrator.optical.workflows.shared import used_port_names_on_node
from orchestrator.optical.workflows.tasks.shared import read_csv_rows

#: Column names of the optical pipe CSV payload, in order.
PIPE_CSV_HEADERS = (
    "pipe_type",
    "node_a_fqdn",
    "port_a_name",
    "node_b_fqdn",
    "port_b_name",
    "optical_pipe_name",
    "provider_name",
)

#: Sub-workflow and product selected by the row's pipe type.
_PIPE_TARGETS: dict[OpticalPipeType, tuple[str, str]] = {
    OpticalPipeType.SPAN: ("create_fiber_span", ProductName.OPTICAL_FIBER_SPAN.value),
    OpticalPipeType.PATCH: ("create_fiber_patch", ProductName.OPTICAL_FIBER_PATCH.value),
    OpticalPipeType.LEASED_SPECTRUM: ("create_leased_spectrum", ProductName.OPTICAL_LEASED_SPECTRUM.value),
}

_FQDN_ADAPTER = TypeAdapter(Fqdn)

Achtung = Annotated[
    str,
    Field(
        "This task will launch a sub-workflow for each optical pipe. "
        "Make sure all referenced nodes exist in the WFO or the sub-workflows will fail! "
        "Check each sub-workflow progress in the Subscriptions page. "
        "If you are sure you want to proceed, replace this warning message with 'CREATE'.",
        title="⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️",
        json_schema_extra={"format": "long"},
    ),
]

CsvData = Annotated[
    str,
    Field(
        ",".join(PIPE_CSV_HEADERS) + "\n",
        title="CSV Data",
        json_schema_extra={"format": "long"},
    ),
]

Delimiter = Annotated[
    str,
    Field(",", description="CSV delimiter character", title="Delimiter"),
]


class PipeCsvRow(TypedDict):
    """One validated row of the optical pipe CSV payload (all values normalized)."""

    line_number: int
    pipe_type: str
    node_a_fqdn: str
    port_a_name: str
    node_b_fqdn: str
    port_b_name: str
    optical_pipe_name: str | None
    provider_name: str | None


class ResolvedPipe(TypedDict):
    """One CSV row resolved against the database, ready for sub-workflow input building."""

    line_number: int
    workflow_name: str
    product_name: str
    is_leased: bool
    node_a_instance_id: str
    node_b_instance_id: str
    port_a_name: str
    port_b_name: str
    optical_pipe_name: str
    provider_name: str | None


class BulkPipeInput(TypedDict):
    """One sub-workflow launch: the target workflow and its ordered form inputs."""

    workflow_name: str
    user_inputs: list[dict[str, Any]]


def _parse_pipe_type(raw: dict[str, str], line_number: int) -> str:
    """Parse and validate the pipe_type column of a pipe CSV row.

    Args:
        raw: The normalized CSV row.
        line_number: The CSV line number, used in error messages.

    Returns:
        The pipe type enum value.

    Raises:
        ValueError: If the pipe type is unknown.
    """
    try:
        return OpticalPipeType(raw["pipe_type"]).value
    except ValueError:
        valid = ", ".join(pipe_type.value for pipe_type in OpticalPipeType)
        msg = f"Invalid pipe_type {raw['pipe_type']!r} at row {line_number}. Valid values are: {valid}"
        raise ValueError(msg) from None


def _parse_pipe_endpoints(raw: dict[str, str], pipe_type: str, line_number: int) -> tuple[str, str, str, str]:
    """Parse and validate the node/port columns of a pipe CSV row.

    Args:
        raw: The normalized CSV row.
        pipe_type: The validated pipe type value.
        line_number: The CSV line number, used in error messages.

    Returns:
        The ``(node_a_fqdn, port_a_name, node_b_fqdn, port_b_name)`` values.

    Raises:
        ValueError: If an FQDN is malformed, a port name is empty, or a
            non-patch pipe has both ends on the same node.
    """
    endpoints = {}
    for key in ("node_a_fqdn", "node_b_fqdn"):
        try:
            endpoints[key] = _FQDN_ADAPTER.validate_python(raw[key])
        except ValueError as exc:
            msg = f"Invalid {key} {raw[key]!r} at row {line_number}: {exc}"
            raise ValueError(msg) from None
    for key in ("port_a_name", "port_b_name"):
        if not raw[key]:
            msg = f"Missing required {key} at row {line_number}"
            raise ValueError(msg)
        endpoints[key] = raw[key]
    same_node = endpoints["node_a_fqdn"].lower() == endpoints["node_b_fqdn"].lower()
    if pipe_type != OpticalPipeType.PATCH.value and same_node:
        msg = f"The two ends of the pipe must be on different nodes at row {line_number}"
        raise ValueError(msg)
    return endpoints["node_a_fqdn"], endpoints["port_a_name"], endpoints["node_b_fqdn"], endpoints["port_b_name"]


def _parse_pipe_provider(raw: dict[str, str], pipe_type: str, line_number: int) -> tuple[str | None, str | None]:
    """Parse and validate the naming columns of a pipe CSV row.

    Args:
        raw: The normalized CSV row.
        pipe_type: The validated pipe type value.
        line_number: The CSV line number, used in error messages.

    Returns:
        The ``(optical_pipe_name, provider_name)`` values, None when empty.

    Raises:
        ValueError: If the provider is missing on a leased spectrum row or
            present on any other pipe type.
    """
    optical_pipe_name = raw["optical_pipe_name"] or None
    provider_name = raw["provider_name"] or None
    if pipe_type == OpticalPipeType.LEASED_SPECTRUM.value:
        if provider_name is None:
            msg = f"Missing required provider_name at row {line_number}"
            raise ValueError(msg)
    elif provider_name is not None:
        msg = f"provider_name is leased-spectrum-only at row {line_number}"
        raise ValueError(msg)
    return optical_pipe_name, provider_name


def _parse_pipe_row(raw: dict[str, str], line_number: int) -> PipeCsvRow:
    """Parse and validate one pipe CSV row (database-free checks only).

    Args:
        raw: The normalized CSV row.
        line_number: The CSV line number, used in error messages.

    Returns:
        The validated row with normalized values.

    Raises:
        ValueError: If any column is missing, malformed, or inconsistent with
            the row's pipe type.
    """
    pipe_type = _parse_pipe_type(raw, line_number)
    node_a_fqdn, port_a_name, node_b_fqdn, port_b_name = _parse_pipe_endpoints(raw, pipe_type, line_number)
    optical_pipe_name, provider_name = _parse_pipe_provider(raw, pipe_type, line_number)
    return PipeCsvRow(
        line_number=line_number,
        pipe_type=pipe_type,
        node_a_fqdn=node_a_fqdn,
        port_a_name=port_a_name,
        node_b_fqdn=node_b_fqdn,
        port_b_name=port_b_name,
        optical_pipe_name=optical_pipe_name,
        provider_name=provider_name,
    )


def _check_pipe_endpoint_reuse(rows: list[PipeCsvRow]) -> None:
    """Reject device-port reuse across rows of the payload.

    Args:
        rows: The parsed pipe CSV rows.

    Raises:
        ValueError: If the same node port is claimed by more than one row end.
    """
    claimed: dict[tuple[str, str], int] = {}
    for row in rows:
        for fqdn, port in ((row["node_a_fqdn"], row["port_a_name"]), (row["node_b_fqdn"], row["port_b_name"])):
            endpoint = (fqdn.lower(), port)
            if endpoint in claimed:
                msg = f"Port {port!r} on {fqdn!r} is claimed at rows {claimed[endpoint]} and {row['line_number']}"
                raise ValueError(msg)
            claimed[endpoint] = row["line_number"]


def parse_pipes_csv(csv_data: str, delimiter: str) -> list[PipeCsvRow]:
    """Parse and validate the optical pipe CSV payload (database-free checks only).

    Args:
        csv_data: The raw CSV payload pasted into the form.
        delimiter: The single-character column delimiter.

    Returns:
        The validated rows, in payload order.

    Raises:
        ValueError: If the headers, a row format, or the intra-payload
            endpoint checks fail.
    """
    parsed = read_csv_rows(csv_data, delimiter, set(PIPE_CSV_HEADERS))
    rows = [_parse_pipe_row(raw, line_number) for line_number, raw in parsed]
    _check_pipe_endpoint_reuse(rows)
    return rows


def _node_instance_id_by_fqdn(fqdn: str, line_number: int) -> str:
    """Resolve a node FQDN to its ACTIVE node block instance id.

    The FQDN is a resource value of the node's management block, so the lookup
    first finds the management instance and then resolves the node block instance
    of the owning subscription.

    Args:
        fqdn: The node FQDN from the CSV row.
        line_number: The CSV line number, used in error messages.

    Returns:
        The subscription instance id of the matching node block.

    Raises:
        ValueError: If the FQDN matches zero or more than one ACTIVE node.
    """
    instances = subscription_instances_by_block_type_and_resource_value(
        cast(str, OpticalModuleNodeManagementBlock.name),
        "optical_module_node_fqdn",
        fqdn,
        [SubscriptionLifecycle.ACTIVE],
    )
    if len(instances) != 1:
        msg = f"Node FQDN {fqdn!r} at row {line_number} matches {len(instances)} ACTIVE nodes"
        raise ValueError(msg)
    return node_instance_id_of_subscription(str(instances[0].subscription_id))


def _check_span_nodes(node_a_instance_id: str, node_b_instance_id: str, line_number: int) -> None:
    """Enforce the fiber span endpoint rules on two resolved nodes.

    A span is OLS-line only and same-vendor by policy: only line-system nodes
    (ROADM / OADM-capable plus amplifiers) can terminate one
    (plain-transponder nodes, including the GX G42, cannot), and the two ends
    must share vendor and platform.

    Args:
        node_a_instance_id: Subscription instance id of the node block hosting end A.
        node_b_instance_id: Subscription instance id of the node block hosting end B.
        line_number: The CSV line number, used in error messages.

    Raises:
        ValueError: If an end cannot terminate a span or the ends differ in
            vendor/platform.
    """
    node_a_block = node_block_from_instance(node_a_instance_id)
    node_b_block = node_block_from_instance(node_b_instance_id)
    for node_block in (node_a_block, node_b_block):
        if node_block.optical_node_role not in SPAN_NODE_ROLES:
            fqdn = node_block.management.optical_module_node_fqdn
            role = node_block.optical_node_role
            msg = f"Node {fqdn!r} at row {line_number} has role {role!r} and cannot terminate a fiber span"
            raise ValueError(msg)
    vendor_platform_a = (
        node_a_block.management.optical_module_node_vendor,
        node_a_block.management.optical_module_node_platform,
    )
    vendor_platform_b = (
        node_b_block.management.optical_module_node_vendor,
        node_b_block.management.optical_module_node_platform,
    )
    if vendor_platform_a != vendor_platform_b:
        msg = f"A fiber span must connect two nodes of the same vendor and platform at row {line_number}"
        raise ValueError(msg)


def _check_pipe_ports_free(node_instance_id: str, port_name: str, line_number: int) -> None:
    """Reject a pipe end whose port is already used by another subscription.

    Args:
        node_instance_id: Subscription instance id of the node block hosting the port.
        port_name: The device port name from the CSV row.
        line_number: The CSV line number, used in error messages.

    Raises:
        ValueError: If the port is in use by an INITIAL, PROVISIONING or
            ACTIVE subscription.
    """
    node_block = node_block_from_instance(node_instance_id)
    if port_name in used_port_names_on_node(node_block):
        fqdn = node_block.management.optical_module_node_fqdn
        msg = f"Port {port_name!r} on {fqdn!r} at row {line_number} is already in use"
        raise ValueError(msg)


def _resolve_pipe_row(row: PipeCsvRow) -> ResolvedPipe:
    """Resolve one parsed CSV row against the database.

    Args:
        row: The parsed pipe CSV row.

    Returns:
        The row with its nodes resolved and its sub-workflow selected.

    Raises:
        ValueError: If a node is not found, the span rules fail, or a port is
            already in use.
    """
    line_number = row["line_number"]
    node_a_instance_id = _node_instance_id_by_fqdn(row["node_a_fqdn"], line_number)
    node_b_instance_id = _node_instance_id_by_fqdn(row["node_b_fqdn"], line_number)
    if row["pipe_type"] == OpticalPipeType.SPAN.value:
        _check_span_nodes(node_a_instance_id, node_b_instance_id, line_number)
    _check_pipe_ports_free(node_a_instance_id, row["port_a_name"], line_number)
    _check_pipe_ports_free(node_b_instance_id, row["port_b_name"], line_number)
    optical_pipe_name = row["optical_pipe_name"]
    if optical_pipe_name is None:
        optical_pipe_name = default_pipe_identifier(
            node_block_from_instance(node_a_instance_id),
            row["port_a_name"],
            node_block_from_instance(node_b_instance_id),
            row["port_b_name"],
        )
    workflow_name, product_name = _PIPE_TARGETS[OpticalPipeType(row["pipe_type"])]
    return ResolvedPipe(
        line_number=line_number,
        workflow_name=workflow_name,
        product_name=product_name,
        is_leased=row["pipe_type"] == OpticalPipeType.LEASED_SPECTRUM.value,
        node_a_instance_id=node_a_instance_id,
        node_b_instance_id=node_b_instance_id,
        port_a_name=row["port_a_name"],
        port_b_name=row["port_b_name"],
        optical_pipe_name=optical_pipe_name,
        provider_name=row["provider_name"],
    )


def _pipe_bulk_input(pipe: ResolvedPipe, customer_id: str) -> BulkPipeInput:
    """Build the ordered sub-workflow form inputs of one resolved pipe row.

    The input list mirrors the shipped create form of the row's product: the
    product dict, the customer dict, the nodes dict, the terminations dict
    (plus the provider dict on leased spectrum) and the empty summary dict.

    Args:
        pipe: The resolved pipe CSV row.
        customer_id: The customer id collected by the bulk task form.

    Returns:
        The target workflow name with its ordered form inputs.
    """
    product_id = str(get_product_by_name(pipe["product_name"]).product_id)
    user_inputs: list[dict[str, Any]] = [
        {"product": product_id},
        {"customer_id": customer_id},
        {"node_a_instance_id": pipe["node_a_instance_id"], "node_b_instance_id": pipe["node_b_instance_id"]},
        {
            "optical_pipe_name": pipe["optical_pipe_name"],
            "port_a_name": pipe["port_a_name"],
            "port_b_name": pipe["port_b_name"],
        },
    ]
    if pipe["is_leased"]:
        user_inputs.append({"provider_name": pipe["provider_name"]})
    user_inputs.append({})
    return BulkPipeInput(workflow_name=pipe["workflow_name"], user_inputs=user_inputs)


def initial_input_form_generator() -> FormGenerator:
    """Collect the customer shared by the batch and the pipe CSV payload."""
    user_input_dict = yield from customer_choice_form_page(title="Bulk create optical pipes")
    user_input = yield BulkCreateOpticalPipesForm
    user_input_dict.update(user_input.model_dump())
    return user_input_dict


class BulkCreateOpticalPipesForm(FormPage):
    """CSV payload form of the bulk optical pipe creation task."""

    achtung: Achtung
    csv_data: CsvData
    delimiter: Delimiter

    @model_validator(mode="after")
    def validate_csv(self) -> "BulkCreateOpticalPipesForm":
        """Fail fast on confirmation or CSV format errors.

        Database checks (node lookup, span rules, port usage) run in the
        resolve step so they report per-row failures with database context.
        """
        if self.achtung != "CREATE":
            msg = "Read the ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ message!"
            raise ValueError(msg)
        parse_pipes_csv(self.csv_data, self.delimiter)
        return self


@step("Resolve nodes and check ports")
def resolve_pipes(csv_data: str, delimiter: str) -> State:
    """Resolve every CSV row against the database.

    Args:
        csv_data: The raw CSV payload from the form.
        delimiter: The CSV delimiter from the form.

    Returns:
        The state with the resolved rows under ``pipes``.
    """
    return {"pipes": [_resolve_pipe_row(row) for row in parse_pipes_csv(csv_data, delimiter)]}


@step("Create workflow input forms")
def create_workflow_inputs(pipes: list[ResolvedPipe], customer_id: str) -> State:
    """Build the ordered sub-workflow form inputs of every resolved row.

    Args:
        pipes: The resolved pipe CSV rows.
        customer_id: The customer id shared by the batch.

    Returns:
        The state with one workflow/input pair per row under ``bulk_inputs``.
    """
    customer = str(customer_id)
    return {"bulk_inputs": [_pipe_bulk_input(pipe, customer) for pipe in pipes]}


@step("Start sub-workflows")
def start_sub_workflows(bulk_inputs: list[BulkPipeInput]) -> State:
    """Launch one pipe create sub-workflow per row, throttled to one per second.

    Args:
        bulk_inputs: The workflow/input pairs built by the previous step.

    Returns:
        The state with the launched process ids under ``process_ids``.
    """
    process_ids: list[UUIDstr] = []
    for bulk_input in bulk_inputs:
        with db.database_scope():
            process_id = start_process(
                bulk_input["workflow_name"], user_inputs=bulk_input["user_inputs"], user="SYSTEM"
            )
            process_ids.append(str(process_id))
        sleep(1)
    return {"process_ids": process_ids}


@workflow(target=Target.SYSTEM, initial_input_form=initial_input_form_generator)
def bulk_create_optical_pipes() -> StepList:
    """Launch one Optical Pipe create sub-workflow per CSV row."""
    return begin >> resolve_pipes >> create_workflow_inputs >> start_sub_workflows >> done
