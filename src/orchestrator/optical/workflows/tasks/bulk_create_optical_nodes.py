"""Bulk creation of Optical Nodes from CSV data.

This module ships the ``bulk_create_optical_nodes`` system task: the operator
pastes a CSV payload, the task validates it and launches one shipped Optical
Node create sub-workflow per row (``create_optical_node_nokia_flexils``,
``create_optical_node_nokia_groove_g30`` or ``create_optical_node_nokia_gx_g42``,
selected from the row's vendor/platform). Sub-workflow progress is tracked in
the Subscriptions page, like any other workflow.

The CSV has one row per node with exactly these headers::

    location_code,vendor,platform,fqdn,dcn_loopback_ip,dcn_interface_ip,gmpls_id,target_id

* ``location_code``: code of an ACTIVE Optical Module Location hosting the node.
* ``vendor``/``platform``: one of the shipped combinations (``Nokia`` +
  ``FlexILS``/``Groove G30``/``GX G42``); selects the sub-workflow.
* ``fqdn``: fully qualified domain name of the node (no derivation, no suffix).
* ``dcn_loopback_ip``/``dcn_interface_ip``: DCN addresses (either may be empty;
  Groove G30 and GX G42 require at least one).
* ``gmpls_id``/``target_id``: Nokia FlexILS GMPLS ID and Target Identifier
  (TID); mandatory on FlexILS rows, forbidden on Groove G30/GX G42 rows.

Validation runs in two layers: the form checks the confirmation, the headers
and the per-row formats (plus duplicates within the CSV); the resolve step
re-checks against the database (location lookup, FQDN/IP/GMPLS-ID/TID
uniqueness over INITIAL, PROVISIONING and ACTIVE subscriptions). The shipped
sub-workflows re-check uniqueness once more at execution time.

This task is the generalized port of the ``bulk_create_optical_devices`` task
of the legacy implementation: the GARR-specific columns (``pop_code``,
``fqdn_prefix_before_pop``, the ``.garr.net`` derivation) and the hardcoded
partner are gone, replaced by ``location_code``/``fqdn`` and the
consumer-configured customer choice (one customer for the whole batch).
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
from orchestrator.optical.db import subscription_instances_by_block_type_and_resource_value
from orchestrator.optical.products import ProductName
from orchestrator.optical.products.product_blocks.optical_location import OpticalModuleLocationBlock
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.flexils import FlexIlsTargetId
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_node.shared.create import (
    validate_gmpls_id_uniqueness,
    validate_management_ips_uniqueness,
    validate_optical_flexils_target_id_uniqueness,
    validate_optical_node_fqdn_uniqueness,
)
from orchestrator.optical.workflows.tasks.shared import read_csv_rows

#: Column names of the optical node CSV payload, in order.
NODE_CSV_HEADERS = (
    "location_code",
    "vendor",
    "platform",
    "fqdn",
    "dcn_loopback_ip",
    "dcn_interface_ip",
    "gmpls_id",
    "target_id",
)

#: Sub-workflow and product selected by the row's (vendor, platform) combination.
_NODE_TARGETS: dict[tuple[Vendor, Platform], tuple[str, str]] = {
    (Vendor.NOKIA, Platform.FLEXILS): (
        "create_optical_node_nokia_flexils",
        ProductName.OPTICAL_NODE_NOKIA_FLEXILS.value,
    ),
    (Vendor.NOKIA, Platform.GROOVE_G30): (
        "create_optical_node_nokia_groove_g30",
        ProductName.OPTICAL_NODE_NOKIA_GROOVE_G30.value,
    ),
    (Vendor.NOKIA, Platform.GX_G42): (
        "create_optical_node_nokia_gx_g42",
        ProductName.OPTICAL_NODE_NOKIA_GX_G42.value,
    ),
}

_FQDN_ADAPTER = TypeAdapter(Fqdn)
_IP_ADAPTER = TypeAdapter(IPAddress)
_TARGET_ID_ADAPTER = TypeAdapter(FlexIlsTargetId)

Achtung = Annotated[
    str,
    Field(
        "This task will launch a sub-workflow for each optical node. "
        "Make sure all referenced locations exist in the WFO or the sub-workflows will fail! "
        "Check each sub-workflow progress in the Subscriptions page. "
        "If you are sure you want to proceed, replace this warning message with 'CREATE'.",
        title="⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️",
        json_schema_extra={"format": "long"},
    ),
]

CsvData = Annotated[
    str,
    Field(
        ",".join(NODE_CSV_HEADERS) + "\n",
        title="CSV Data",
        json_schema_extra={"format": "long"},
    ),
]

Delimiter = Annotated[
    str,
    Field(",", description="CSV delimiter character", title="Delimiter"),
]


class NodeCsvRow(TypedDict):
    """One validated row of the optical node CSV payload (all values normalized)."""

    line_number: int
    location_code: str
    vendor: str
    platform: str
    fqdn: str
    dcn_loopback_ip: str | None
    dcn_interface_ip: str | None
    gmpls_id: str | None
    target_id: str | None


class ResolvedNode(TypedDict):
    """One CSV row resolved against the database, ready for sub-workflow input building."""

    line_number: int
    workflow_name: str
    product_name: str
    is_flexils: bool
    location_instance_id: str
    fqdn: str
    dcn_loopback_ip: str | None
    dcn_interface_ip: str | None
    gmpls_id: str | None
    target_id: str | None


class BulkNodeInput(TypedDict):
    """One sub-workflow launch: the target workflow and its ordered form inputs."""

    workflow_name: str
    user_inputs: list[dict[str, Any]]


def _validated_ip(value: str, field: str, line_number: int) -> str | None:
    """Validate an optional IP field, returning None for empty values.

    Args:
        value: The stripped CSV value.
        field: The column name, used in error messages.
        line_number: The CSV line number, used in error messages.

    Returns:
        The validated IP address, or None when the value is empty.

    Raises:
        ValueError: If the non-empty value is not a valid IPv4/IPv6 address.
    """
    if not value:
        return None
    try:
        return _IP_ADAPTER.validate_python(value)
    except ValueError as exc:
        msg = f"Invalid {field} {value!r} at row {line_number}: {exc}"
        raise ValueError(msg) from None


def _required_ip(value: str, field: str, line_number: int) -> str:
    """Validate a mandatory IP field.

    Args:
        value: The stripped CSV value.
        field: The column name, used in error messages.
        line_number: The CSV line number, used in error messages.

    Returns:
        The validated IP address.

    Raises:
        ValueError: If the value is empty or not a valid IPv4/IPv6 address.
    """
    validated = _validated_ip(value, field, line_number)
    if validated is None:
        msg = f"Missing required {field} at row {line_number}"
        raise ValueError(msg)
    return validated


def _required_target_id(value: str, line_number: int) -> str:
    """Validate the mandatory FlexILS Target Identifier field.

    Args:
        value: The stripped CSV value.
        line_number: The CSV line number, used in error messages.

    Returns:
        The validated Target Identifier.

    Raises:
        ValueError: If the value is empty or not a valid Target Identifier.
    """
    if not value:
        msg = f"Missing required target_id at row {line_number}"
        raise ValueError(msg)
    try:
        return _TARGET_ID_ADAPTER.validate_python(value)
    except ValueError as exc:
        msg = f"Invalid target_id {value!r} at row {line_number}: {exc}"
        raise ValueError(msg) from None


def _parse_node_vendor_platform(raw: dict[str, str], line_number: int) -> tuple[str, str]:
    """Parse and validate the vendor/platform columns of a node CSV row.

    Args:
        raw: The normalized CSV row.
        line_number: The CSV line number, used in error messages.

    Returns:
        The ``(vendor, platform)`` enum values.

    Raises:
        ValueError: If the vendor or platform is unknown, or their combination
            has no shipped node product.
    """
    try:
        vendor = Vendor(raw["vendor"])
    except ValueError:
        valid = ", ".join(vendor.value for vendor in Vendor)
        msg = f"Invalid vendor {raw['vendor']!r} at row {line_number}. Valid values are: {valid}"
        raise ValueError(msg) from None
    try:
        platform = Platform(raw["platform"])
    except ValueError:
        valid = ", ".join(platform.value for platform in Platform)
        msg = f"Invalid platform {raw['platform']!r} at row {line_number}. Valid values are: {valid}"
        raise ValueError(msg) from None
    if (vendor, platform) not in _NODE_TARGETS:
        supported = ", ".join(f"{vendor.value} {platform.value}" for vendor, platform in _NODE_TARGETS)
        msg = (
            f"Unsupported vendor/platform combination {vendor.value!r}/{platform.value!r} at row {line_number}. "
            f"Bulk creation supports: {supported}"
        )
        raise ValueError(msg)
    return vendor.value, platform.value


def _parse_node_row(raw: dict[str, str], line_number: int) -> NodeCsvRow:
    """Parse and validate one node CSV row (database-free checks only).

    Args:
        raw: The normalized CSV row.
        line_number: The CSV line number, used in error messages.

    Returns:
        The validated row with normalized values.

    Raises:
        ValueError: If any column is missing, malformed, or inconsistent with
            the row's vendor/platform combination.
    """
    vendor, platform = _parse_node_vendor_platform(raw, line_number)
    is_flexils = (vendor, platform) == (Vendor.NOKIA.value, Platform.FLEXILS.value)
    try:
        fqdn = _FQDN_ADAPTER.validate_python(raw["fqdn"])
    except ValueError as exc:
        msg = f"Invalid fqdn {raw['fqdn']!r} at row {line_number}: {exc}"
        raise ValueError(msg) from None
    loopback_ip = _validated_ip(raw["dcn_loopback_ip"], "dcn_loopback_ip", line_number)
    interface_ip = _validated_ip(raw["dcn_interface_ip"], "dcn_interface_ip", line_number)
    if not is_flexils and not (loopback_ip or interface_ip):
        msg = f"At least one of dcn_loopback_ip or dcn_interface_ip must be provided at row {line_number}"
        raise ValueError(msg)
    gmpls_id: str | None
    target_id: str | None
    if is_flexils:
        gmpls_id = _required_ip(raw["gmpls_id"], "gmpls_id", line_number)
        target_id = _required_target_id(raw["target_id"], line_number)
    else:
        if raw["gmpls_id"] or raw["target_id"]:
            msg = f"gmpls_id and target_id are Nokia FlexILS-only at row {line_number}"
            raise ValueError(msg)
        gmpls_id = None
        target_id = None
    if not raw["location_code"]:
        msg = f"Missing required location_code at row {line_number}"
        raise ValueError(msg)
    return NodeCsvRow(
        line_number=line_number,
        location_code=raw["location_code"],
        vendor=vendor,
        platform=platform,
        fqdn=fqdn,
        dcn_loopback_ip=loopback_ip,
        dcn_interface_ip=interface_ip,
        gmpls_id=gmpls_id,
        target_id=target_id,
    )


def _claim(seen: dict[str, int], value: str, label: str, line_number: int) -> None:
    """Record a unique CSV value, failing on duplicates within the payload.

    Args:
        seen: Map of already-seen values to their line numbers.
        value: The value to record.
        label: The column label, used in error messages.
        line_number: The CSV line number, used in error messages.

    Raises:
        ValueError: If the value was already seen on another row.
    """
    if value in seen:
        msg = f"{label} {value!r} is duplicated at rows {seen[value]} and {line_number}"
        raise ValueError(msg)
    seen[value] = line_number


def _check_node_duplicates(rows: list[NodeCsvRow]) -> None:
    """Reject FQDN, IP, GMPLS ID and Target Identifier reuse within the payload.

    Args:
        rows: The parsed node CSV rows.

    Raises:
        ValueError: If any unique value appears on more than one row.
    """
    seen_fqdns: dict[str, int] = {}
    seen_ips: dict[str, int] = {}
    seen_gmpls_ids: dict[str, int] = {}
    seen_target_ids: dict[str, int] = {}
    for row in rows:
        line_number = row["line_number"]
        _claim(seen_fqdns, row["fqdn"].lower(), "FQDN", line_number)
        for ip in (row["dcn_loopback_ip"], row["dcn_interface_ip"]):
            if ip is not None:
                _claim(seen_ips, ip, "IP", line_number)
        if row["gmpls_id"] is not None:
            _claim(seen_gmpls_ids, row["gmpls_id"], "GMPLS ID", line_number)
        if row["target_id"] is not None:
            _claim(seen_target_ids, row["target_id"], "Target Identifier", line_number)


def parse_nodes_csv(csv_data: str, delimiter: str) -> list[NodeCsvRow]:
    """Parse and validate the optical node CSV payload (database-free checks only).

    Args:
        csv_data: The raw CSV payload pasted into the form.
        delimiter: The single-character column delimiter.

    Returns:
        The validated rows, in payload order.

    Raises:
        ValueError: If the headers, a row format, or the intra-payload
            uniqueness checks fail.
    """
    parsed = read_csv_rows(csv_data, delimiter, set(NODE_CSV_HEADERS))
    rows = [_parse_node_row(raw, line_number) for line_number, raw in parsed]
    _check_node_duplicates(rows)
    return rows


def _location_instance_id_by_code(location_code: str, line_number: int) -> str:
    """Resolve a location code to its ACTIVE location block instance id.

    Args:
        location_code: The location code from the CSV row.
        line_number: The CSV line number, used in error messages.

    Returns:
        The subscription instance id of the matching location block.

    Raises:
        ValueError: If the code matches zero or more than one ACTIVE location.
    """
    instances = subscription_instances_by_block_type_and_resource_value(
        cast(str, OpticalModuleLocationBlock.name),
        "location_code",
        location_code,
        [SubscriptionLifecycle.ACTIVE],
    )
    if len(instances) != 1:
        msg = f"Location code {location_code!r} at row {line_number} matches {len(instances)} ACTIVE locations"
        raise ValueError(msg)
    return str(instances[0].subscription_instance_id)


def _resolve_node_row(row: NodeCsvRow) -> ResolvedNode:
    """Resolve one parsed CSV row against the database.

    Args:
        row: The parsed node CSV row.

    Returns:
        The row with its location resolved and its sub-workflow selected.

    Raises:
        ValueError: If the location is not found, or the FQDN, a DCN IP, the
            GMPLS ID or the Target Identifier is already in use.
    """
    line_number = row["line_number"]
    location_instance_id = _location_instance_id_by_code(row["location_code"], line_number)
    try:
        validate_optical_node_fqdn_uniqueness(row["fqdn"])
    except ValueError as exc:
        msg = f"Row {line_number}: {exc}"
        raise ValueError(msg) from None
    try:
        validate_management_ips_uniqueness(
            [ip for ip in (row["dcn_loopback_ip"], row["dcn_interface_ip"]) if ip is not None]
        )
    except ValueError as exc:
        msg = f"Row {line_number}: {exc}"
        raise ValueError(msg) from None
    is_flexils = (row["vendor"], row["platform"]) == (Vendor.NOKIA.value, Platform.FLEXILS.value)
    if is_flexils:
        try:
            validate_gmpls_id_uniqueness(cast(str, row["gmpls_id"]))
        except ValueError as exc:
            msg = f"Row {line_number}: {exc}"
            raise ValueError(msg) from None
        try:
            validate_optical_flexils_target_id_uniqueness(cast(str, row["target_id"]))
        except ValueError as exc:
            msg = f"Row {line_number}: {exc}"
            raise ValueError(msg) from None
    workflow_name, product_name = _NODE_TARGETS[(Vendor(row["vendor"]), Platform(row["platform"]))]
    return ResolvedNode(
        line_number=line_number,
        workflow_name=workflow_name,
        product_name=product_name,
        is_flexils=is_flexils,
        location_instance_id=location_instance_id,
        fqdn=row["fqdn"],
        dcn_loopback_ip=row["dcn_loopback_ip"],
        dcn_interface_ip=row["dcn_interface_ip"],
        gmpls_id=row["gmpls_id"],
        target_id=row["target_id"],
    )


def _node_bulk_input(node: ResolvedNode, customer_id: str) -> BulkNodeInput:
    """Build the ordered sub-workflow form inputs of one resolved node row.

    The input list mirrors the shipped create form of the row's product: the
    product dict, the customer dict, one dict per create page (location,
    management, plus the FlexILS vendor page) and the empty summary dict.

    Args:
        node: The resolved node CSV row.
        customer_id: The customer id collected by the bulk task form.

    Returns:
        The target workflow name with its ordered form inputs.
    """
    product_id = str(get_product_by_name(node["product_name"]).product_id)
    user_inputs: list[dict[str, Any]] = [
        {"product": product_id},
        {"customer_id": customer_id},
        {"location_instance_id": node["location_instance_id"]},
        {
            "optical_module_node_fqdn": node["fqdn"],
            "optical_module_node_dcn_loopback_ip": node["dcn_loopback_ip"],
            "optical_module_node_dcn_interface_ip": node["dcn_interface_ip"],
        },
    ]
    if node["is_flexils"]:
        user_inputs.append(
            {
                "optical_flexils_gmpls_id": node["gmpls_id"],
                "optical_flexils_target_id": node["target_id"],
            }
        )
    user_inputs.append({})
    return BulkNodeInput(workflow_name=node["workflow_name"], user_inputs=user_inputs)


def initial_input_form_generator() -> FormGenerator:
    """Collect the customer shared by the batch and the node CSV payload."""
    user_input_dict = yield from customer_choice_form_page(title="Bulk create optical nodes")
    user_input = yield BulkCreateOpticalNodesForm
    user_input_dict.update(user_input.model_dump())
    return user_input_dict


class BulkCreateOpticalNodesForm(FormPage):
    """CSV payload form of the bulk optical node creation task."""

    achtung: Achtung
    csv_data: CsvData
    delimiter: Delimiter

    @model_validator(mode="after")
    def validate_csv(self) -> "BulkCreateOpticalNodesForm":
        """Fail fast on confirmation or CSV format errors.

        Database checks (location lookup, uniqueness) run in the resolve step
        so they report per-row failures with database context.
        """
        if self.achtung != "CREATE":
            msg = "Read the ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ message!"
            raise ValueError(msg)
        parse_nodes_csv(self.csv_data, self.delimiter)
        return self


@step("Resolve locations and check duplicates")
def resolve_nodes(csv_data: str, delimiter: str) -> State:
    """Resolve every CSV row against the database.

    Args:
        csv_data: The raw CSV payload from the form.
        delimiter: The CSV delimiter from the form.

    Returns:
        The state with the resolved rows under ``nodes``.
    """
    return {"nodes": [_resolve_node_row(row) for row in parse_nodes_csv(csv_data, delimiter)]}


@step("Create workflow input forms")
def create_workflow_inputs(nodes: list[ResolvedNode], customer_id: str) -> State:
    """Build the ordered sub-workflow form inputs of every resolved row.

    Args:
        nodes: The resolved node CSV rows.
        customer_id: The customer id shared by the batch.

    Returns:
        The state with one workflow/input pair per row under ``bulk_inputs``.
    """
    customer = str(customer_id)
    return {"bulk_inputs": [_node_bulk_input(node, customer) for node in nodes]}


@step("Start sub-workflows")
def start_sub_workflows(bulk_inputs: list[BulkNodeInput]) -> State:
    """Launch one node create sub-workflow per row, throttled to one per second.

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
def bulk_create_optical_nodes() -> StepList:
    """Launch one Optical Node create sub-workflow per CSV row."""
    return begin >> resolve_nodes >> create_workflow_inputs >> start_sub_workflows >> done
