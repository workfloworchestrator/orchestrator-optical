"""Tests for the device sessions: one per device within a step or a form submit, reused by the next one."""

import inspect

import pytest
from pydantic import field_validator
from pydantic_forms.core import FormPage, post_form
from pydantic_forms.exceptions import FormNotCompleteError, FormValidationError
from pydantic_forms.types import FormGenerator, State

from orchestrator.optical.hal import sessions as sessions_module
from orchestrator.optical.hal.sessions import (
    DeviceSessions,
    close_idle_device_sessions,
    device_sessions,
    shared_session,
)
from orchestrator.optical.settings import get_settings
from orchestrator.optical.workflows.shared import retryable_form

pytestmark = pytest.mark.unit


class _Client:
    """A device session that records how many were opened and which are closed."""

    opened: list["_Client"] = []  # noqa: RUF012 - the shared log of the test

    def __init__(self, key: str) -> None:
        self.key = key
        self.closed = False
        _Client.opened.append(self)

    def close(self) -> None:
        self.closed = True


@pytest.fixture(autouse=True)
def _reset() -> None:
    _Client.opened.clear()


def _client(key: str = "node-a") -> _Client:
    return shared_session(key, lambda: _Client(key))


def test_outside_a_scope_every_call_opens_a_session() -> None:
    assert _client() is not _client()
    assert len(_Client.opened) == 2


def test_a_scope_shares_one_session_per_device_and_leaves_them_open_at_its_end() -> None:
    with device_sessions():
        a, b = _client("node-a"), _client("node-b")
        assert _client("node-a") is a

    assert [client.key for client in _Client.opened] == ["node-a", "node-b"]
    assert not a.closed
    assert not b.closed


def test_consecutive_scopes_reuse_the_session_of_a_device() -> None:
    with device_sessions():
        first = _client()
    with device_sessions():
        assert _client() is first
    assert len(_Client.opened) == 1


def test_a_session_in_use_is_not_shared_with_a_concurrent_scope() -> None:
    running, other = DeviceSessions(), DeviceSessions()
    with running.active():
        first = _client()
    with other.active():  # e.g. another workflow on the same node, in another thread
        second = _client()
    assert second is not first

    running.release()
    other.release()
    with device_sessions():
        assert _client() in (first, second)
    assert len(_Client.opened) == 2


def test_a_nested_scope_reuses_the_enclosing_one() -> None:
    with device_sessions() as outer:
        with device_sessions() as inner:
            client = _client()
        assert inner is outer
        assert _client() is client
    assert len(_Client.opened) == 1


@device_sessions()
def _failing_step() -> None:
    _client()
    raise RuntimeError


def test_a_failing_scope_closes_its_sessions_instead_of_leaving_them_for_reuse() -> None:
    with pytest.raises(RuntimeError):
        _failing_step()
    assert _Client.opened[0].closed
    with device_sessions():
        assert _client() is not _Client.opened[0]


def test_idle_sessions_are_closed_when_their_idle_time_elapses(monkeypatch: pytest.MonkeyPatch) -> None:
    now = [0.0]
    monkeypatch.setattr(sessions_module.time, "monotonic", lambda: now[0])
    with device_sessions():
        client = _client()

    now[0] = get_settings().device_session_idle_seconds - 1
    sessions_module._idle_sessions.close_expired()  # noqa: SLF001 - what the timer runs
    assert not client.closed

    now[0] += 1
    sessions_module._idle_sessions.close_expired()  # noqa: SLF001
    assert client.closed
    with device_sessions():
        assert _client() is not client


def test_no_session_is_kept_when_the_idle_time_is_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "device_session_idle_seconds", 0)
    with device_sessions():
        client = _client()
    assert client.closed


def test_an_idle_session_dropped_by_the_device_is_replaced() -> None:
    with device_sessions():
        dropped = shared_session("node-a", lambda: _Client("node-a"))
    with device_sessions():
        client = shared_session("node-a", lambda: _Client("node-a"), lambda candidate: candidate is not dropped)
    assert client is not dropped
    assert dropped.closed


def test_closing_the_idle_sessions_closes_them_all() -> None:
    with device_sessions():
        a, b = _client("node-a"), _client("node-b")
    close_idle_device_sessions()
    assert a.closed
    assert b.closed


class _BrokenClient(_Client):
    def close(self) -> None:
        msg = "connection reset"
        raise OSError(msg)


def test_a_session_failing_to_close_does_not_mask_the_others() -> None:
    with device_sessions():
        shared_session("broken", lambda: _BrokenClient("broken"))
        healthy = _client("healthy")

    close_idle_device_sessions()

    assert healthy.closed


def test_the_decorator_keeps_the_step_signature_and_runs_the_step_in_a_scope() -> None:
    @device_sessions()
    def a_step(subscription_id: str) -> State:
        assert _client() is _client()
        return {"subscription_id": subscription_id}

    # Core's ``@step`` injects the arguments from ``inspect.signature`` of the decorated function.
    assert list(inspect.signature(a_step).parameters) == ["subscription_id"]
    assert a_step("s") == {"subscription_id": "s"}
    assert a_step("s") == {"subscription_id": "s"}  # the next step finds the session open
    assert len(_Client.opened) == 1


class _NodePage(FormPage):
    node: str

    @field_validator("node")
    @classmethod
    def _reachable(cls, value: str) -> str:
        _client(value)
        return value


class _PortPage(FormPage):
    port: str


@retryable_form
def _form() -> FormGenerator:
    _client()
    first = yield _NodePage
    _client(first.node)
    second = yield _PortPage
    return {**first.model_dump(), **second.model_dump()}


def _generator(_state: State) -> FormGenerator:
    return (yield from _form())


def test_a_form_submit_shares_one_session_per_device_and_leaves_them_open() -> None:
    with pytest.raises(FormNotCompleteError):
        post_form(_generator, {}, [{"node": "node-a"}])

    # The generator, the validator and the next page all reached node-a: one session.
    assert [client.key for client in _Client.opened] == ["node-a"]
    assert not _Client.opened[0].closed


def test_the_next_form_submits_reuse_the_sessions() -> None:
    with pytest.raises(FormNotCompleteError):
        post_form(_generator, {}, [{"node": "node-b"}])
    result = post_form(_generator, {}, [{"node": "node-b"}, {"port": "1"}])

    assert result == {"node": "node-b", "port": "1"}
    assert [client.key for client in _Client.opened] == ["node-a", "node-b"]


@retryable_form
def _failing_form() -> FormGenerator:
    _client()
    msg = "device went away"
    raise OSError(msg)
    yield _PortPage


def test_a_form_submit_hitting_an_unexpected_error_closes_its_sessions() -> None:
    def generator(_state: State) -> FormGenerator:
        return (yield from _failing_form())

    with pytest.raises(FormValidationError):
        post_form(generator, {}, [])

    assert _Client.opened[0].closed
