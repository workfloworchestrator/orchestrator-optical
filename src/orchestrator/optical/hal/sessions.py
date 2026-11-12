"""Device sessions shared within a scope: one session per node, closed when the scope ends.

Every connection to a Groove G30 or GX G42 node is a full SSH login plus a NETCONF
hello. Within a scope the client factories (``get_g30_client``, ``get_g42_client``)
return the session already open to the node instead of opening another one, and the
scope closes all of them when it ends. Outside a scope every call opens its own
session.

The scopes are a workflow step (``@device_sessions()`` under ``@step``) and a form
submit (:func:`orchestrator.optical.workflows.shared.retryable_form`). A session is
therefore never shared by two workflows, two threads or two HTTP requests: the NETCONF
locks and commits of a workflow never mix with another's, and no session outlives the
work it was opened for.
"""

from collections.abc import Callable, Hashable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Self

from structlog import get_logger

__all__ = ["DeviceSessions", "device_sessions", "shared_session"]

logger = get_logger(__name__)


class DeviceSessions:
    """The device sessions of a scope: one per node, opened on first use, closed by :meth:`close`."""

    def __init__(self) -> None:
        """Start with no session open."""
        self._clients: dict[Hashable, Any] = {}

    @contextmanager
    def active(self) -> Iterator[Self]:
        """Make the client factories use these sessions within the block; the sessions stay open after it."""
        token = _active.set(self)
        try:
            yield self
        finally:
            _active.reset(token)

    def session[ClientT](self, key: Hashable, connect: Callable[[], ClientT]) -> ClientT:
        """Return the session of ``key``, opening it with ``connect`` on first use."""
        if key not in self._clients:
            self._clients[key] = connect()
        return self._clients[key]

    def close(self) -> None:
        """Close every open session. A session failing to close is logged, never raised."""
        clients, self._clients = self._clients, {}
        for key, client in clients.items():
            try:
                client.close()
            except Exception:  # noqa: BLE001 - closing must never mask the outcome of the scope
                logger.warning("Could not close a device session", device=repr(key), exc_info=True)


_active: ContextVar[DeviceSessions | None] = ContextVar("optical_device_sessions", default=None)


@contextmanager
def device_sessions() -> Iterator[DeviceSessions]:
    """Share one session per device within the block and close them all when it ends.

    Use it as ``with device_sessions():`` or as the decorator ``@device_sessions()``,
    placed under ``@step``. Nested scopes reuse the enclosing one, which keeps closing.
    """
    enclosing = _active.get()
    if enclosing is not None:
        yield enclosing
        return
    sessions = DeviceSessions()
    try:
        with sessions.active():
            yield sessions
    finally:
        sessions.close()


def shared_session[ClientT](key: Hashable, connect: Callable[[], ClientT]) -> ClientT:
    """Return the session of ``key`` in the active scope, opened on first use; outside a scope, a new session.

    Args:
        key: Identifies the device and the client type (e.g. the client class and the node's management IPs).
        connect: Opens a new session.

    Returns:
        The connected client.
    """
    sessions = _active.get()
    return connect() if sessions is None else sessions.session(key, connect)
