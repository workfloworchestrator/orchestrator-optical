"""Device sessions kept open across workflow steps and form submits: one login per node, not one per use.

Every connection to a Groove G30 or GX G42 node is a full SSH login plus a NETCONF
hello. The sessions are therefore kept by the (operating system) process:

- A **scope** (a workflow step: ``@device_sessions()`` under ``@step``; a form submit:
  :func:`orchestrator.optical.workflows.shared.retryable_form`) borrows the session of
  each node it reaches, on first use, and gives them back when it ends. Within the
  scope the client factories (``get_g30_client``, ``get_g42_client``) keep returning
  that session.
- A session given back stays open, idle, for ``OPTICAL_DEVICE_SESSION_IDLE_SECONDS``
  and is handed to the next scope reaching the node: the next step of the workflow,
  the next submit of a form. Idle sessions are closed when that time elapses and when
  the process exits.

A session is borrowed by one scope at a time, so it is never used by two threads at
once: the steps of a workflow run one after the other and reuse the same session,
while a workflow or a form submit running at the same time on the same node finds it
borrowed and opens its own (given back and reused the same way). The NETCONF locks
and commits of a workflow never mix with another's.

Forms only read from the devices, never write; that is what lets a session they used
be handed to anyone next. A scope that ends with an error does not give its sessions
back: they are closed, so a retry starts from a new login.

Outside a scope every factory call opens its own session.
"""

import atexit
import os
import threading
import time
from collections.abc import Callable, Hashable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Self

from structlog import get_logger

from orchestrator.optical.settings import get_settings

__all__ = ["DeviceSessions", "close_idle_device_sessions", "device_sessions", "shared_session"]

logger = get_logger(__name__)


def _close(key: Hashable, client: Any) -> None:
    """Close a session. A session failing to close is logged, never raised."""
    try:
        client.close()
    except Exception:  # noqa: BLE001 - closing must never mask the outcome of the caller
        logger.warning("Could not close a device session", device=repr(key), exc_info=True)


def _always_alive(_client: Any) -> bool:
    return True


class _IdleSessions:
    """The open sessions no scope is using, per device. Thread-safe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._idle: dict[Hashable, list[tuple[Any, float]]] = {}
        self._timer: threading.Timer | None = None

    def take(self, key: Hashable, is_alive: Callable[[Any], bool]) -> Any | None:
        """Remove and return the most recently used live idle session of ``key``, or ``None``."""
        while True:
            with self._lock:
                entries = self._idle.get(key)
                if not entries:
                    self._idle.pop(key, None)
                    return None
                client, _ = entries.pop()
            if is_alive(client):
                return client
            _close(key, client)  # dropped by the device while idle

    def put(self, key: Hashable, client: Any) -> None:
        """Keep ``client`` open for the idle time of the settings (closed at once when that is 0)."""
        idle_seconds = get_settings().device_session_idle_seconds
        if idle_seconds <= 0:
            _close(key, client)
            return
        with self._lock:
            self._idle.setdefault(key, []).append((client, time.monotonic() + idle_seconds))
            self._schedule(idle_seconds)

    def close_expired(self) -> None:
        """Close the sessions whose idle time elapsed."""
        now = time.monotonic()
        expired: list[tuple[Hashable, Any]] = []
        with self._lock:
            self._timer = None
            remaining: list[float] = []
            for key in list(self._idle):
                kept = [(client, deadline) for client, deadline in self._idle[key] if deadline > now]
                expired += [(key, client) for client, deadline in self._idle[key] if deadline <= now]
                remaining += [deadline for _, deadline in kept]
                if kept:
                    self._idle[key] = kept
                else:
                    del self._idle[key]
            if remaining:
                self._schedule(min(remaining) - now)
        for key, client in expired:
            _close(key, client)

    def close_all(self) -> None:
        """Close every idle session."""
        with self._lock:
            idle, self._idle = self._idle, {}
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        for key, entries in idle.items():
            for client, _ in entries:
                _close(key, client)

    def forget(self) -> None:
        """Drop the idle sessions without closing them (a forked child: they belong to the parent)."""
        self._lock = threading.Lock()
        self._idle = {}
        self._timer = None

    def _schedule(self, delay: float) -> None:
        """Arrange for :meth:`close_expired` to run (lock held); one pending timer at a time."""
        if self._timer is None:
            self._timer = threading.Timer(max(delay, 0.0), self.close_expired)
            self._timer.daemon = True
            self._timer.start()


_idle_sessions = _IdleSessions()
atexit.register(_idle_sessions.close_all)
os.register_at_fork(after_in_child=_idle_sessions.forget)


def close_idle_device_sessions() -> None:
    """Close every idle device session of this process now (shutdown hooks, tests)."""
    _idle_sessions.close_all()


class DeviceSessions:
    """The device sessions borrowed by a scope: one per node, taken on first use, given back by :meth:`release`."""

    def __init__(self) -> None:
        """Start with no session borrowed."""
        self._clients: dict[Hashable, Any] = {}
        self.failed = False
        """Set when the scope hit an unexpected error: :meth:`release` then closes the sessions."""

    @contextmanager
    def active(self) -> Iterator[Self]:
        """Make the client factories use these sessions within the block; they stay borrowed after it."""
        token = _active.set(self)
        try:
            yield self
        finally:
            _active.reset(token)

    def session[ClientT](
        self, key: Hashable, connect: Callable[[], ClientT], is_alive: Callable[[Any], bool] = _always_alive
    ) -> ClientT:
        """Return the session of ``key``: the one already borrowed, else an idle one, else a new one."""
        if key not in self._clients:
            client = _idle_sessions.take(key, is_alive)
            self._clients[key] = connect() if client is None else client
        return self._clients[key]

    def release(self) -> None:
        """Give the sessions back to be reused; close them instead when the scope :attr:`failed`."""
        clients, self._clients = self._clients, {}
        for key, client in clients.items():
            if self.failed:
                _close(key, client)
            else:
                _idle_sessions.put(key, client)


_active: ContextVar[DeviceSessions | None] = ContextVar("optical_device_sessions", default=None)


@contextmanager
def device_sessions() -> Iterator[DeviceSessions]:
    """Share one session per device within the block; give them back for the next scope when it ends.

    Use it as ``with device_sessions():`` or as the decorator ``@device_sessions()``,
    placed under ``@step``. Nested scopes reuse the enclosing one, which keeps releasing.
    A block ending with an exception closes its sessions instead of giving them back.
    """
    enclosing = _active.get()
    if enclosing is not None:
        yield enclosing
        return
    sessions = DeviceSessions()
    try:
        with sessions.active():
            yield sessions
    except BaseException:
        sessions.failed = True
        raise
    finally:
        sessions.release()


def shared_session[ClientT](
    key: Hashable, connect: Callable[[], ClientT], is_alive: Callable[[Any], bool] = _always_alive
) -> ClientT:
    """Return the session of ``key`` in the active scope; outside a scope, a new session.

    Args:
        key: Identifies the device and the client type (e.g. the client class and the node's management IPs).
        connect: Opens a new session.
        is_alive: Tells whether an idle session is still usable (one the device dropped is closed, not reused).

    Returns:
        The connected client.
    """
    sessions = _active.get()
    return connect() if sessions is None else sessions.session(key, connect, is_alive)
