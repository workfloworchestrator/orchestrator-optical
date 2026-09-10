.PHONY: install lint typecheck test-fast test-db test coverage ci

install:
	uv sync --all-groups

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run ty check
	uv run pyrefly check

test-fast:
	uv run pytest -m "not db"

test-db:
	uv run pytest -m db

test:
	uv run pytest

coverage:
	uv run pytest --cov=orchestrator.optical --cov-report=json:coverage.json --cov-report=xml:coverage.xml && uv run python scripts/coverage_ratchet.py

ci:
	$(MAKE) lint typecheck test-fast test-db
