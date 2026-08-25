"""Database migrations for the Workflow Orchestrator Optical module.

The module ships its catalog (products, product blocks, resource types, workflows) as
**coded programmatic migrations**: one generated Alembic revision per release, chained
linearly onto a pinned orchestrator-core schema revision. Consumers add the shipped
``versions/schema`` directory to their Alembic ``version_locations`` (via
:func:`add_optical_module_migrations` or a single ``alembic.ini`` entry), merge the
optical head with their own ``data`` head once, and ``upgrade head`` from then on.

Until the module reaches a stable release (the models are still being finalised) the
shipped ``versions/schema`` directory is intentionally empty and consumers provision the
catalog with the orchestrator-core CLI wizards instead; the generation pipeline
(:mod:`orchestrator.optical.migrations.generate`) is the mechanism that will produce the
checked-in baseline at 1.0.
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

from pathlib import Path

from alembic.config import Config

import orchestrator.core.migrations

__all__ = [
    "add_optical_module_migrations",
    "alembic_cfg",
    "version_schema_path",
]


def version_schema_path() -> Path:
    """Return the absolute path to the shipped ``versions/schema`` migration directory.

    The directory is empty until the first stable release ships the baseline migration.
    Consumers point Alembic's ``version_locations`` at this directory, e.g. from their own
    ``alembic.ini`` or by calling :func:`add_optical_module_migrations` on their config.
    """
    return Path(__file__).parent / "versions" / "schema"


def add_optical_module_migrations(config: Config) -> Config:
    """Append the shipped optical migration directory to an Alembic config's ``version_locations``.

    Args:
        config: The consumer's Alembic config (``script_location`` must point at the
            orchestrator-core migration environment).

    Returns:
        The same config object, mutated in place, with the optical ``versions/schema``
        directory appended to ``version_locations`` (space-separated, as orchestrator-core
        itself appends its own schema directory).
    """
    current = config.get_main_option("version_locations") or ""
    separator = " " if current and not current.endswith(" ") else ""
    config.set_main_option("version_locations", f"{current}{separator}{version_schema_path()}")
    return config


def alembic_cfg() -> Config:
    """Return an Alembic config that runs the shipped optical migrations.

    The config reuses the orchestrator-core migration environment (``env.py`` and
    ``script.py.mako`` from ``orchestrator.core.migrations``) and extends its
    ``version_locations`` with the shipped optical ``versions/schema`` directory, mirroring
    how orchestrator-core itself wires its own schema migrations. The database URL is set
    by the core ``env.py`` from ``orchestrator.core.settings`` at runtime.
    """
    core_migrations_dir = Path(orchestrator.core.migrations.__file__).parent
    config = Config(str(Path(__file__).parent / "alembic.ini"))
    config.set_main_option("script_location", str(core_migrations_dir))
    config.set_main_option(
        "version_locations",
        f"{core_migrations_dir / 'versions' / 'schema'} {version_schema_path()}",
    )
    return config
