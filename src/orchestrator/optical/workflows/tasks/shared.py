"""Shared CSV helpers for the bulk-task workflows.

This module ships the CSV parsing shared by the bulk creation tasks: reading a
pasted CSV payload with a configurable delimiter, checking its headers against
the required columns of the task and normalizing its rows. Per-row semantic
validation lives in the task modules, as pure functions next to their row
types, so it stays unit-testable without a database.
"""

import csv
from io import StringIO


def read_csv_rows(
    csv_data: str,
    delimiter: str,
    required_headers: set[str],
    optional_headers: frozenset[str] = frozenset(),
) -> list[tuple[int, dict[str, str]]]:
    """Parse a CSV payload into normalized rows with their line numbers.

    Headers and values are stripped of surrounding whitespace; missing values
    become empty strings, and so do the values of an optional column the
    payload leaves out. Columns are matched by header name, in any order.
    Fully empty lines are skipped. The returned line
    numbers are the true CSV line numbers (the header is line 1), so validation
    errors point at the offending spreadsheet row.

    Args:
        csv_data: The raw CSV payload pasted into the form.
        delimiter: The single-character column delimiter.
        required_headers: The column names the payload must have.
        optional_headers: The column names the payload may leave out.

    Returns:
        A list of ``(line_number, row)`` pairs, one per non-empty data row.

    Raises:
        ValueError: If the delimiter is not a single character, the payload is
            empty, the headers are missing/unknown/duplicated, a row has more
            values than headers, or there are no data rows.
    """
    if len(delimiter) != 1:
        msg = f"Delimiter must be a single character, got {delimiter!r}"
        raise ValueError(msg)
    if not csv_data.strip():
        msg = "CSV content is empty"
        raise ValueError(msg)

    reader = csv.DictReader(StringIO(csv_data), delimiter=delimiter)
    if not reader.fieldnames:
        msg = "CSV content is empty"
        raise ValueError(msg)

    headers = [(header or "").strip() for header in reader.fieldnames]
    if len(set(headers)) != len(headers):
        msg = f"Duplicated CSV headers: {', '.join(sorted(headers))}"
        raise ValueError(msg)
    unknown = [header for header in headers if header not in required_headers | optional_headers]
    if unknown:
        msg = f"Unknown CSV headers: {', '.join(unknown)}"
        raise ValueError(msg)
    missing = sorted(required_headers - set(headers))
    if missing:
        msg = f"Missing CSV headers: {', '.join(missing)}"
        raise ValueError(msg)

    rows: list[tuple[int, dict[str, str]]] = []
    for record in reader:
        line_number = reader.line_num
        if None in record:
            msg = f"Row {line_number} has more values than the {len(headers)} headers"
            raise ValueError(msg)
        row = dict.fromkeys(optional_headers, "")
        row.update(
            {(key or "").strip(): (value.strip() if isinstance(value, str) else "") for key, value in record.items()}
        )
        if all(not value for value in row.values()):
            continue
        rows.append((line_number, row))

    if not rows:
        msg = "CSV contains no data rows"
        raise ValueError(msg)
    return rows
