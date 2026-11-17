"""Bulk creation of Optical Nodes from CSV data.

This module ships the ``bulk_create_optical_nodes`` system task: the operator
pastes a CSV payload, the task validates it and launches one shipped Optical
Node create sub-workflow per row (``create_optical_node_nokia_flexils``,
``create_optical_node_nokia_groove_g30`` or ``create_optical_node_nokia_gx_g42``,
selected from the row's vendor/platform). Sub-workflow progress is tracked in
the Subscriptions page, like any other workflow.

The CSV has one row per node and a header line naming its columns (matched by
name, in any order)::

    location_code,vendor,platform,name,dcn_loopback_ip,dcn_interface_ip,target_id

* ``location_code`` (required): code of an ACTIVE Optical Module Location
  hosting the node.
* ``vendor``/``platform`` (required): one of the shipped combinations
  (``Nokia`` + ``FlexILS``/``Groove G30``/``GX G42``); selects the sub-workflow.
* ``name`` (optional): name of the node, stored as given; when empty, the name
  read from the device is used (as prefilled by the shipped create forms).
* ``dcn_loopback_ip``/``dcn_interface_ip``: DCN addresses (either may be empty;
  Groove G30 and GX G42 require at least one).
* ``target_id``: Nokia FlexILS Target Identifier (TID); mandatory on FlexILS
  rows, forbidden on Groove G30/GX G42 rows. The GMPLS ID is read from the device.

Only the first three columns must be in the header line: the others may be left
out when no row needs them. The form page spells these rules out for the
operator (``BulkCreateOpticalNodesForm``: one line per column, one example row
per platform).

One task serves the three node families on purpose: the rows differ by a single
column (``target_id``), and a site is usually commissioned with mixed platforms
from one inventory export.

Validation runs in two layers: the form checks the confirmation, the headers
and the per-row formats (plus duplicates within the CSV); the resolve step
re-checks against the database (location lookup, name/IP/TID
uniqueness over INITIAL, PROVISIONING and ACTIVE subscriptions). The shipped
sub-workflows re-check uniqueness once more at execution time.

This task is the generalized port of the ``bulk_create_optical_devices`` task
of the legacy implementation: the GARR-specific columns (``pop_code``,
``fqdn_prefix_before_pop``, the ``.garr.net`` derivation) and the hardcoded
partner are gone, replaced by ``location_code``/``name`` and the
consumer-configured customer choice (one customer for the whole batch).
"""

from collections.abc import Iterable
from time import sleep
from typing import Annotated, Any, TypedDict, cast

from pydantic import Field, TypeAdapter, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import markdown

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
from orchestrator.optical.utils.custom_types.flexils import FlexIlsTargetId
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.utils.custom_types.node_name import OpticalNodeName
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_node.shared.create import (
    validate_management_ips_uniqueness,
    validate_optical_flexils_target_id_uniqueness,
    validate_optical_node_name_uniqueness,
)
from orchestrator.optical.workflows.shared import retryable_form
from orchestrator.optical.workflows.tasks.shared import read_csv_rows

#: Columns every optical node CSV payload must have.
NODE_CSV_REQUIRED_HEADERS = ("location_code", "vendor", "platform")

#: Columns a payload may leave out when none of its rows needs them.
NODE_CSV_OPTIONAL_HEADERS = ("name", "dcn_loopback_ip", "dcn_interface_ip", "target_id")

#: Column names of the optical node CSV payload, in the order prefilled in the form.
NODE_CSV_HEADERS = NODE_CSV_REQUIRED_HEADERS + NODE_CSV_OPTIONAL_HEADERS

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


def _one_of(values: Iterable[str]) -> str:
    """Return the values as an English alternative: ``"A"``, ``"A or B"``, ``"A, B or C"``."""
    *head, last = values
    return f"{', '.join(head)} or {last}" if head else last


_NODE_NAME_ADAPTER = TypeAdapter(OpticalNodeName)
_IP_ADAPTER = TypeAdapter(IPAddress)
_TARGET_ID_ADAPTER = TypeAdapter(FlexIlsTargetId)
_INSTRUCTIONS = f"""## Instructions

Write **one line per node** below the header line.

- Columns are matched by their header name, so their order is flexible.
- Leave a value empty when it does not apply to the node.
- Columns that are not needed by any node can be removed entirely, including their headers.

### Column Definitions

| Column | Description |
| --- | --- |
| `location_code` | **REQUIRED.** Code of the Optical Location hosting the node. The location must already exist and be active. |
| `vendor` | **REQUIRED.** {_one_of(dict.fromkeys(vendor.value for vendor, _ in _NODE_TARGETS))}. |
| `platform` | **REQUIRED.** {_one_of(platform.value for _, platform in _NODE_TARGETS)}. Must be spelled exactly as specified. |
| `name` | Optional. Name displayed for the node in the orchestrator. Leave empty to use the name configured on the device. |
| `dcn_loopback_ip` | IPv4 or IPv6 management address used to reach the node. |
| `dcn_interface_ip` | IPv4 or IPv6 management address used to reach the node. |

### Platform-Specific Requirements

**Groove G30 and GX G42**

- At least one of `dcn_loopback_ip` or `dcn_interface_ip` is **REQUIRED**.

**FlexILS**

- Both `dcn_loopback_ip` and `dcn_interface_ip` are optional.
- If neither is provided, the node is reached through the gateway node closest to its location.
- `target_id` is **REQUIRED**.
- `target_id` is the FlexILS Target Identifier (TID).
- It can contain up to 20 letters, digits, hyphens, dots, or underscores.
- It must start with a letter.

**Groove G30 and GX G42**

- `target_id` must be left empty.

### Examples

**FlexILS**

csv

```csv
loc-01,Nokia,FlexILS,,,,FLEX-01
````

Groove G30

csv

csv

```csv
loc-01,Nokia,Groove G30,g30-01,192.0.2.11,198.51.100.11,
```

GX G42 (name read from the device)

csv

csv

```csv
loc-02,Nokia,GX G42,,,198.51.100.22,
```

### ⚠️ Warning

- This task will launch a sub-workflow for each optical node.
- Make sure all referenced locations already exist in WFO. Otherwise, the sub-workflows will fail.
- You can monitor the progress of each sub-workflow on the Subscriptions page."""

Markdown = markdown(content=_INSTRUCTIONS)
Achtung = Annotated[
    str,
    Field(
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
        description="Keep the header line and add one line per node below it.",
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
    name: str | None
    dcn_loopback_ip: str | None
    dcn_interface_ip: str | None
    target_id: str | None


class ResolvedNode(TypedDict):
    """One CSV row resolved against the database, ready for sub-workflow input building."""

    line_number: int
    workflow_name: str
    product_name: str
    is_flexils: bool
    location_instance_id: str
    name: str | None
    dcn_loopback_ip: str | None
    dcn_interface_ip: str | None
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
    name: str | None = None
    if raw["name"]:
        try:
            name = _NODE_NAME_ADAPTER.validate_python(raw["name"])
        except ValueError as exc:
            msg = f"Invalid name {raw['name']!r} at row {line_number}: {exc}"
            raise ValueError(msg) from None
    loopback_ip = _validated_ip(raw["dcn_loopback_ip"], "dcn_loopback_ip", line_number)
    interface_ip = _validated_ip(raw["dcn_interface_ip"], "dcn_interface_ip", line_number)
    if not is_flexils and not (loopback_ip or interface_ip):
        msg = f"At least one of dcn_loopback_ip or dcn_interface_ip must be provided at row {line_number}"
        raise ValueError(msg)
    target_id: str | None = None
    if is_flexils:
        target_id = _required_target_id(raw["target_id"], line_number)
    elif raw["target_id"]:
        msg = f"target_id is Nokia FlexILS-only at row {line_number}"
        raise ValueError(msg)
    if not raw["location_code"]:
        msg = f"Missing required location_code at row {line_number}"
        raise ValueError(msg)
    return NodeCsvRow(
        line_number=line_number,
        location_code=raw["location_code"],
        vendor=vendor,
        platform=platform,
        name=name,
        dcn_loopback_ip=loopback_ip,
        dcn_interface_ip=interface_ip,
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
    """Reject node name, IP and Target Identifier reuse within the payload.

    Args:
        rows: The parsed node CSV rows.

    Raises:
        ValueError: If any unique value appears on more than one row.
    """
    seen_names: dict[str, int] = {}
    seen_ips: dict[str, int] = {}
    seen_target_ids: dict[str, int] = {}
    for row in rows:
        line_number = row["line_number"]
        if row["name"] is not None:
            _claim(seen_names, row["name"], "name", line_number)
        for ip in (row["dcn_loopback_ip"], row["dcn_interface_ip"]):
            if ip is not None:
                _claim(seen_ips, ip, "IP", line_number)
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
    parsed = read_csv_rows(csv_data, delimiter, set(NODE_CSV_REQUIRED_HEADERS), frozenset(NODE_CSV_OPTIONAL_HEADERS))
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
        ValueError: If the location is not found, or the node name, a DCN IP or
            the Target Identifier is already in use.
    """
    line_number = row["line_number"]
    location_instance_id = _location_instance_id_by_code(row["location_code"], line_number)
    if row["name"] is not None:
        try:
            validate_optical_node_name_uniqueness(row["name"])
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
        name=row["name"],
        dcn_loopback_ip=row["dcn_loopback_ip"],
        dcn_interface_ip=row["dcn_interface_ip"],
        target_id=row["target_id"],
    )


def _node_bulk_input(node: ResolvedNode, customer_id: str) -> BulkNodeInput:
    """Build the ordered sub-workflow form inputs of one resolved node row.

    The input list mirrors the shipped create form of the row's product: the
    product dict, the customer dict, one dict per create page (location, the
    FlexILS vendor page, management, identity) and the empty summary dict. A
    row without a name leaves the identity page empty, which keeps the name
    read from the device.

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
    ]
    if node["is_flexils"]:
        user_inputs.append({"optical_flexils_target_id": node["target_id"]})
    user_inputs += [
        {
            "optical_module_node_management_loopback_ip": node["dcn_loopback_ip"],
            "optical_module_node_management_ip": node["dcn_interface_ip"],
        },
        {"optical_module_node_name": node["name"]} if node["name"] is not None else {},
        {},
    ]
    return BulkNodeInput(workflow_name=node["workflow_name"], user_inputs=user_inputs)


@retryable_form
def initial_input_form_generator() -> FormGenerator:
    """Collect the customer shared by the batch and the node CSV payload."""
    user_input_dict = yield from customer_choice_form_page(title="Bulk create optical nodes")
    user_input = yield BulkCreateOpticalNodesForm
    user_input_dict.update(user_input.model_dump())
    return user_input_dict


class BulkCreateOpticalNodesForm(FormPage):
    """CSV payload form of the bulk optical node creation task.

    The labels above the payload tell the operator what each column holds and
    when it is required: one label per column, then one example row per
    platform (labels are single lines in the UI).
    """

    markdown: Markdown
    csv_data: CsvData
    delimiter: Delimiter
    achtung: Achtung

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
