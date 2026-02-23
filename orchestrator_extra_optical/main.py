"""Metodo di avviamento del core dell'applicazione: gestisce chiamate REST e ridistribuisce le esecuzioni."""

import typer
from celery import Celery
from orchestrator import OrchestratorCore
from orchestrator.cli.main import app as core_cli
from orchestrator.services.tasks import initialise_celery
from orchestrator.settings import AppSettings, app_settings
from structlog import get_logger

import products  # noqa: F401 Side-effects
import schedules  # noqa: F401 Side-effects
import workflows  # noqa: F401 Side-effects
from auth.oidc import CustomOIDCAuth
from graphql_federation import CUSTOM_GRAPHQL_MODELS
from settings import celery_settings, garr_settings

logger = get_logger(__name__)


def init_app(orchestrator_settings: AppSettings) -> OrchestratorCore:
    """Inizializza l'applicazione e lo scheduler Celery."""
    app = OrchestratorCore(base_settings=orchestrator_settings)
    if garr_settings.OAUTH2_ACTIVE:
        app.register_authentication(CustomOIDCAuth())
    app.register_graphql(graphql_models=CUSTOM_GRAPHQL_MODELS)
    celery = Celery(
        app_settings.SERVICE_NAME,
        broker=celery_settings.broker_url,
        backend=celery_settings.result_backend,
        include=["orchestrator.services.tasks"],
    )
    celery.conf.update(
        result_expires=celery_settings.result_expires,
        # foza esecuzione dei task in core e in modo sincrono al posto che passarli al worker
        task_always_eager=app_settings.TESTING,
        # propaga le exception al chiamante
        task_eager_propagates=app_settings.TESTING,
    )
    initialise_celery(celery)

    return app


def init_cli_app() -> typer.Typer:
    """Inizializza la CLI includendo eventuali comandi custom."""
    return core_cli()


# logger.debug("Starting the app with the following settings", app_settings=str(app_settings))  # noqa: ERA001
app = init_app(app_settings)

if __name__ == "__main__":
    init_cli_app()
