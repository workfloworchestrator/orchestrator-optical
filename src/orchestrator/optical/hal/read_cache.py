"""Device reads remembered across the submits of an input form.

A form generator is replayed from its first page on every submit, so a five-page form
asks the device the same things five times over (discovery of the node, its ports, its
internal connectivity, ...), and every answer costs seconds. The read dispatchers of the
HAL marked with :func:`cached_device_read` therefore remember their result, per
(operating system) process, for ``OPTICAL_DEVICE_READ_CACHE_SECONDS``:

- **Only form submits use it.** A result is looked up and stored only inside a
  :class:`DeviceReads` scope, which :func:`orchestrator.optical.workflows.shared.retryable_form`
  opens around a submit. Workflow steps (and any other caller) always read the device:
  what a form showed is checked again, live, by the steps that act on it.
- **A result is at most that many seconds old**, counted from the read (a hit does not
  extend it), whichever form or user reads it next: forms never write to a device, so
  what one read is as good for another.
- **A rejected submit forgets what it read** (:meth:`DeviceReads.forget`): after an error
  the user fixes the cause, possibly on the device, and submits again, which must not be
  answered from before the fix.
- **Errors are never remembered**, only results.

The key of a result is the dispatcher plus its arguments; a product block counts as its
``subscription_instance_id`` and, for a node, the management IPs it is reached at. Results
are copied on the way in and out, so a caller may change what it gets.
"""

import inspect
import os
import threading
import time
from collections.abc import Callable, Hashable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from functools import wraps
from typing import Any, Self

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.optical.settings import get_settings

__all__ = ["DeviceReads", "cached_device_read", "clear_device_read_cache"]


class _Results:
    """The remembered results with their expiry. Thread-safe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._results: dict[Hashable, tuple[Any, float]] = {}

    def get(self, key: Hashable) -> tuple[Any] | None:
        """Return the live result of ``key`` wrapped in a 1-tuple (a result may be ``None``), else ``None``."""
        with self._lock:
            entry = self._results.get(key)
            if entry is None or entry[1] <= time.monotonic():
                return None
            return (entry[0],)

    def put(self, key: Hashable, value: Any, seconds: float) -> None:
        """Remember ``value`` for ``seconds``; the expired results are dropped on the way."""
        now = time.monotonic()
        with self._lock:
            self._results = {k: entry for k, entry in self._results.items() if entry[1] > now}
            self._results[key] = (value, now + seconds)

    def discard(self, keys: set[Hashable]) -> None:
        with self._lock:
            for key in keys:
                self._results.pop(key, None)

    def clear(self) -> None:
        # A new lock as well: after a fork the inherited one may be held by a thread that does not exist here.
        self._lock = threading.Lock()
        self._results = {}


_results = _Results()
os.register_at_fork(after_in_child=_results.clear)


def clear_device_read_cache() -> None:
    """Forget every remembered device read of this process (tests, shutdown hooks)."""
    _results.clear()


class DeviceReads:
    """The scope of a form submit: within it, the marked device reads are answered from memory when possible."""

    def __init__(self) -> None:
        """Start with nothing read."""
        self._keys: set[Hashable] = set()

    @contextmanager
    def active(self) -> Iterator[Self]:
        """Let the marked device reads within the block use the remembered results."""
        token = _active.set(self)
        try:
            yield self
        finally:
            _active.reset(token)

    def forget(self) -> None:
        """Drop every result this scope read or reused, so that the next submit asks the devices again."""
        keys, self._keys = self._keys, set()
        _results.discard(keys)

    def _used(self, key: Hashable) -> None:
        self._keys.add(key)


_active: ContextVar[DeviceReads | None] = ContextVar("optical_device_reads", default=None)


def _key_part(value: Any) -> Hashable:
    """Return what identifies an argument of a device read."""
    if isinstance(value, ProductBlockModel):
        management = getattr(value, "management", None)
        return (
            type(value).__name__,
            value.subscription_instance_id,
            str(getattr(management, "optical_module_node_management_loopback_ip", None)),
            str(getattr(management, "optical_module_node_management_ip", None)),
        )
    if isinstance(value, list | tuple):
        return tuple(_key_part(item) for item in value)
    return value


def cached_device_read[**P, T](read: Callable[P, T]) -> Callable[P, T]:
    """Mark a read-only HAL dispatcher whose result a form submit may take from memory (see the module).

    Mark only operations that read: the call is skipped altogether on a hit. Outside a
    :class:`DeviceReads` scope, or with ``OPTICAL_DEVICE_READ_CACHE_SECONDS=0``, the
    decorated function behaves exactly as the plain one.
    """
    signature = inspect.signature(read)
    name = (read.__module__, getattr(read, "__qualname__", repr(read)))

    @wraps(read)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        scope = _active.get()
        seconds = get_settings().device_read_cache_seconds
        if scope is None or seconds <= 0:
            return read(*args, **kwargs)
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        key = (*name, *(_key_part(value) for value in bound.arguments.values()))
        try:
            hash(key)
        except TypeError:  # an argument that cannot identify a read: do not guess, read
            return read(*args, **kwargs)
        scope._used(key)  # noqa: SLF001 - the scope and the decorator are one mechanism
        remembered = _results.get(key)
        if remembered is not None:
            return deepcopy(remembered[0])
        value = read(*args, **kwargs)
        _results.put(key, deepcopy(value), seconds)
        return value

    return wrapper
