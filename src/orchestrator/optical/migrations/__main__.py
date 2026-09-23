"""Command-line entrypoint for the optical migration generation pipeline.

``python -m orchestrator.optical.migrations`` derives the shipped catalog
(products, product blocks, resource types, workflows) from the shipped models and renders
the Alembic revision that provisions it. The pipeline is used by maintainers to produce
the checked-in baseline at the first stable release, and by CI to verify the applied
migrations never drift from the models.

Example (verify the shipped models produce a drift-free catalog against a scratch DB):

    OPTICAL_TEST_PG_URL=postgresql+psycopg://... python -m orchestrator.optical.migrations --verify

Example (write the baseline into the shipped ``versions/schema`` directory):

    python -m orchestrator.optical.migrations --commit

The database URL for ``--verify`` comes from ``--db-url``, else ``OPTICAL_TEST_PG_URL``,
else ``DATABASE_URI``.
"""

# Copyright 2026 GARR, GÉANT.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import tempfile
from pathlib import Path

import orchestrator.core.db as core_db
import orchestrator.core.settings as core_settings
import orchestrator.optical.products  # noqa: F401  # register the shipped product types in the registry
from orchestrator.optical.migrations import version_schema_path
from orchestrator.optical.migrations.generate import (
    apply_migrations,
    generate_plan,
    pinned_core_revision,
    verify_no_drift,
    write_migration,
)


def _configure_database(db_url: str) -> None:
    """Point the orchestrator-core runtime at ``db_url`` and initialise the database."""
    settings = core_settings.AppSettings(DATABASE_URI=db_url)
    core_settings.app_settings = settings
    core_db.init_database(settings)


def main() -> None:
    """Parse arguments and run the generation pipeline."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="Write the baseline into the shipped versions/schema")
    parser.add_argument("--out", type=Path, help="Write the migration into this directory instead")
    parser.add_argument("--verify", action="store_true", help="Apply pending migrations and fail on model drift")
    parser.add_argument("--db-url", help="Database URL for --verify (default: OPTICAL_TEST_PG_URL or DATABASE_URI)")
    parser.add_argument("--message", default="optical baseline", help="Revision message")
    args = parser.parse_args()

    plan = generate_plan()
    if plan.is_empty:
        print("No catalog or workflows derived from the shipped models; nothing to generate.")  # noqa: T201
        return

    down_revision = pinned_core_revision()
    target_dir: Path | None = None
    if args.commit:
        target_dir = version_schema_path()
    elif args.out is not None:
        target_dir = args.out

    if target_dir is not None:
        path = write_migration(plan, target_dir, down_revision=down_revision, message=args.message)
        print(f"Wrote {path} (revision {plan.revision}, down_revision {down_revision})")  # noqa: T201
    elif not args.verify:
        print(f"Dry run: revision {plan.revision}, down_revision {down_revision}")  # noqa: T201

    if args.verify:
        db_url = args.db_url or os.environ.get("OPTICAL_TEST_PG_URL") or os.environ.get("DATABASE_URI")
        if not db_url:
            parser.error("--verify requires --db-url, OPTICAL_TEST_PG_URL or DATABASE_URI")
        if target_dir is None:
            # Self-contained check: write the plan to a scratch directory and apply that.
            target_dir = Path(tempfile.mkdtemp(prefix="optical-migrations-"))
            write_migration(plan, target_dir, down_revision=down_revision, message=args.message)
        _configure_database(db_url)
        apply_migrations(target_dir)
        verify_no_drift()
        print("Migrations applied; database catalog is drift-free.")  # noqa: T201


if __name__ == "__main__":
    main()
