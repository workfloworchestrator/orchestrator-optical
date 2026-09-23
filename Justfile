# Justfile for the WFO Optical module.
#
# Fits the orchestrator-core toolchain: the same `just <recipe>` entry points
# contributors already use in orchestrator-core (`just pytest`, `just sync`).
# Run `just --list` to discover the available recipes.

# List possible recipes
default:
    @just --list

# Install/sync virtual environment with UV
sync:
    uv sync --all-groups

alias install := sync

# Lint (line-length 120, google docstrings); ported code must be 0-findings
lint:
    uv run ruff check .
    uv run ruff format --check .

# Type check (pyrefly is the harder gate)
typecheck:
    uv run ty check
    uv run pyrefly check

# DB-free test lane
test-fast:
    uv run pytest -m "not db"

# DB-backed test lane (needs Postgres, see OPTICAL_TEST_PG_URL in CI)
test-db:
    uv run pytest -m db

# Full suite (both lanes)
test:
    uv run pytest

# Run pytest with arbitrary args, e.g. `just pytest -vx -k foo`
pytest *args:
    uv run pytest {{ args }}

# DB-free lane with per-family coverage ratchet
coverage:
    uv run pytest --cov=orchestrator.optical --cov-report=json:coverage.json --cov-report=xml:coverage.xml && uv run python scripts/coverage_ratchet.py

# Full suite (both lanes) with coverage for the diff-cover gate (mirrors CI test-integration).
# NOTE: the -m expression is hardcoded (not passed via `just pytest ...`) because the generic
# `pytest *args` passthrough cannot preserve the quoting around "db or not db".
test-integration:
    uv run pytest -m "db or not db" --cov=orchestrator.optical --cov-report=xml:coverage.xml

# Full local gate
ci: lint typecheck test-fast test-db
