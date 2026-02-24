import orchestrator_extra_optical
from alembic.config import Config
from structlog import get_logger
from os.path import dirname

logger = get_logger(__name__)


def add_optical_module_migrations(config: Config) -> None:
    """Configure database migrations for the WFO Optical Module."""
    logger.info("Adding WFO Optical Module database migrations to Alembic.")

    current_version_locations = config.get_main_option("version_locations") or ""
    logger.debug(f"Current Alembic version locations: '{current_version_locations}'")
    optical_schema_versions = f"{dirname(__file__)}/versions/schema"
    config.set_main_option(
        "version_locations",
        f"{current_version_locations};{optical_schema_versions}",
    )

    logger.debug(f"Alembic version locations after change: {config.get_main_option("version_locations")}")

module_location = dirname(orchestrator_extra_optical.__file__)
migration_dir = "migrations"

def alembic_cfg() -> Config:
    cfg = Config("alembic.ini")
    version_locations = cfg.get_main_option("version_locations")
    cfg.set_main_option(
        "version_locations", f"{version_locations} {module_location}/{migration_dir}/versions/schema"
    )
    logger.info("Version Locations", locations=cfg.get_main_option("version_locations"))
    return cfg
