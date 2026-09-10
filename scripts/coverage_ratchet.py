#!/usr/bin/env python
"""Per-family coverage ratchet for the optical module.

Reads a coverage.py JSON report, aggregates coverage per immediate child of
``src/orchestrator/optical/`` (``products``, ``hal``, ``settings.py``, ...), and
fails when a family drops below its floor declared in ``coverage-floors.toml``.

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


def load_floors(path: Path) -> dict[str, int]:
    """Load the ``[floors]`` table from a TOML file."""
    with path.open("rb") as handle:
        document = tomllib.load(handle)
    floors = document.get("floors", {})
    if not isinstance(floors, dict):
        sys.exit(f"invalid floors file {path}: [floors] must be a table")
    return {str(name): int(value) for name, value in floors.items()}


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
    floors = load_floors(floors_path)

    families = sorted(set(actual) | set(floors))
    width = max([len(name) for name in families] + [len("family")])
    print(f"{'family'.ljust(width)} | {'actual%':>8} | {'floor':>5} | status")
    print(f"{'-' * width}-+----------+-------+-------")

    failures: list[str] = []
    missing: list[str] = []
    for family in families:
        value = actual.get(family)
        floor = floors.get(family)
        actual_text = "n/a" if value is None else f"{value:8.2f}"
        floor_text = "n/a" if floor is None else f"{floor:5d}"
        if floor is None:
            status = "NO FLOOR"
            missing.append(family)
        elif value is None:
            status = "not measured (omitted)"
        elif value + 1e-9 < floor:
            status = "FAIL"
            failures.append(family)
        else:
            status = "ok"
        print(f"{family.ljust(width)} | {actual_text} | {floor_text} | {status}")

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
