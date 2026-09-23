#!/usr/bin/env python
"""Per-family coverage ratchet for the optical module.

Reads a coverage.py JSON report, aggregates coverage per immediate child of
``src/orchestrator/optical/`` (``products``, ``hal``, ``settings.py``, ...), and
fails when a family drops below its floor declared in ``coverage-floors.toml``.

Families listed in the top-level ``exclude`` list of the floors file are shown
for visibility but never gated: this is for modules a lane cannot observe (e.g.
``db.py`` holds live-Postgres query helpers the DB-free lane never executes;
its new code is gated by the diff-cover patch gate in the DB lane instead).

Floors are a ratchet: raise them as coverage improves, never lower them silently.
Stdlib only; no third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_MARKER = "orchestrator/optical/"
DEFAULT_REPORT = "coverage.json"
DEFAULT_FLOORS = "coverage-floors.toml"


def family_of(path: str) -> str | None:
    """Return the immediate child (dir or file) of the optical package for a file path."""
    normalized = path.replace("\\", "/")
    marker_index = normalized.rfind(PACKAGE_MARKER)
    if marker_index == -1:
        return None
    relative = normalized[marker_index + len(PACKAGE_MARKER) :]
    if not relative:
        return None
    return relative.split("/", 1)[0]


def aggregate(files: dict[str, Any]) -> dict[str, float]:
    """Aggregate branch-aware coverage percentage per family from the report file list."""
    totals: dict[str, list[int]] = {}
    for path, entry in files.items():
        family = family_of(path)
        if family is None:
            continue
        summary = entry.get("summary", {})
        covered = int(summary.get("covered_lines", 0)) + int(summary.get("covered_branches", 0))
        total = int(summary.get("num_statements", 0)) + int(summary.get("num_branches", 0))
        bucket = totals.setdefault(family, [0, 0])
        bucket[0] += covered
        bucket[1] += total

    percentages: dict[str, float] = {}
    for family, (covered, total) in totals.items():
        percentages[family] = 100.0 if total == 0 else 100.0 * covered / total
    return percentages


def load_floors(path: Path) -> tuple[dict[str, int], set[str]]:
    """Load the ``[floors]`` table and the top-level ``exclude`` list from a TOML file.

    Args:
        path: Path to the floors TOML file.

    Returns:
        A ``(floors, excluded)`` pair of per-family floors and excluded families.
    """
    with path.open("rb") as handle:
        document = tomllib.load(handle)
    floors = document.get("floors", {})
    if not isinstance(floors, dict):
        sys.exit(f"invalid floors file {path}: [floors] must be a table")
    excluded_raw = document.get("exclude", [])
    if not isinstance(excluded_raw, list) or not all(isinstance(name, str) for name in excluded_raw):
        sys.exit(f"invalid floors file {path}: 'exclude' must be a list of strings")
    return {str(name): int(value) for name, value in floors.items()}, set(excluded_raw)


def check_family(value: float | None, floor: int | None) -> tuple[str, bool, bool]:
    """Decide the ratchet status of one family.

    Args:
        value: Measured coverage percentage, or None when the family was not measured.
        floor: Configured floor, or None when the family has no floor.

    Returns:
        A ``(status, is_failure, is_missing_floor)`` triple for the report table.
    """
    if floor is None:
        return "NO FLOOR", False, True
    if value is None:
        return "not measured (omitted)", False, False
    if value + 1e-9 < floor:
        return "FAIL", True, False
    return "ok", False, False


def main(argv: list[str] | None = None) -> int:
    """Print the per-family table and return non-zero if any family is below its floor."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", nargs="?", default=DEFAULT_REPORT, help="coverage.py JSON report path")
    parser.add_argument("--floors", default=DEFAULT_FLOORS, help="coverage floors TOML path")
    args = parser.parse_args(argv)

    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = REPO_ROOT / report_path
    floors_path = Path(args.floors)
    if not floors_path.is_absolute():
        floors_path = REPO_ROOT / floors_path

    if not report_path.is_file():
        print(f"error: coverage report not found: {report_path}", file=sys.stderr)
        return 2
    if not floors_path.is_file():
        print(f"error: floors file not found: {floors_path}", file=sys.stderr)
        return 2

    report = json.loads(report_path.read_text())
    actual = aggregate(report.get("files", {}))
    floors, excluded = load_floors(floors_path)

    families = sorted((set(actual) | set(floors)) - excluded)
    excluded_measured = sorted(set(actual) & excluded)
    width = max([len(name) for name in families + excluded_measured] + [len("family")])
    print(f"{'family'.ljust(width)} | {'actual%':>8} | {'floor':>5} | status")
    print(f"{'-' * width}-+----------+-------+-------")

    failures: list[str] = []
    missing: list[str] = []
    for family in families:
        value = actual.get(family)
        floor = floors.get(family)
        status, is_failure, is_missing_floor = check_family(value, floor)
        if is_failure:
            failures.append(family)
        if is_missing_floor:
            missing.append(family)
        actual_text = "n/a" if value is None else f"{value:8.2f}"
        floor_text = "n/a" if floor is None else f"{floor:5d}"
        print(f"{family.ljust(width)} | {actual_text} | {floor_text} | {status}")
    for family in excluded_measured:
        value = actual[family]
        print(f"{family.ljust(width)} | {value:8.2f} | {'n/a':>5} | excluded (gated per-patch in the DB lane)")

    if missing:
        print(f"\nmissing floors (add them to {floors_path.name}): {', '.join(missing)}", file=sys.stderr)
    if failures or missing:
        below = ", ".join(f"{name}={actual[name]:.2f}%" for name in failures)
        if below:
            print(f"coverage below floor: {below}", file=sys.stderr)
        return 1

    print("\nall families meet their floor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
