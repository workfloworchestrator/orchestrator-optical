"""Tests for the device-sessions scope: one session per device within a step or a form submit."""

import inspect

import pytest
from pydantic import field_validator
from pydantic_forms.core import FormPage, post_form
from pydantic_forms.exceptions import FormNotCompleteError
from pydantic_forms.types import FormGenerator, State

from orchestrator.optical.hal.sessions import DeviceSessions, device_sessions, shared_session
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


def test_a_scope_shares_one_session_per_device_and_closes_them_at_its_end() -> None:
    with device_sessions():
        a, b = _client("node-a"), _client("node-b")
        assert _client("node-a") is a
        assert not a.closed

    assert [client.key for client in _Client.opened] == ["node-a", "node-b"]
    assert a.closed
    assert b.closed


def test_a_nested_scope_reuses_the_enclosing_one() -> None:
    with device_sessions() as outer:
        with device_sessions() as inner:
            client = _client()
        assert inner is outer
        assert not client.closed  # still the enclosing scope's session
        assert _client() is client
    assert client.closed


@device_sessions()
def _failing_step() -> None:
    _client()
    raise RuntimeError


def test_the_scope_closes_its_sessions_when_the_block_fails() -> None:
    with pytest.raises(RuntimeError):
        _failing_step()
    assert _Client.opened[0].closed


class _BrokenClient(_Client):
    def close(self) -> None:
        msg = "connection reset"
        raise OSError(msg)


def test_a_session_failing_to_close_does_not_mask_the_others() -> None:
    sessions = DeviceSessions()
    with sessions.active():
        shared_session("broken", lambda: _BrokenClient("broken"))
        healthy = _client("healthy")

    sessions.close()

    assert healthy.closed


def test_the_decorator_keeps_the_step_signature_and_runs_the_step_in_a_scope() -> None:
    @device_sessions()
    def a_step(subscription_id: str) -> State:
        assert _client() is _client()
        return {"subscription_id": subscription_id}

    # Core's ``@step`` injects the arguments from ``inspect.signature`` of the decorated function.
    assert list(inspect.signature(a_step).parameters) == ["subscription_id"]
    assert a_step("s") == {"subscription_id": "s"}
    assert len(_Client.opened) == 1
    assert _Client.opened[0].closed


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


def test_a_form_submit_shares_one_session_per_device_and_closes_them() -> None:
    with pytest.raises(FormNotCompleteError):
        post_form(_generator, {}, [{"node": "node-a"}])

    # The generator, the validator and the next page all reached node-a: one session.
    assert [client.key for client in _Client.opened] == ["node-a"]
    assert all(client.closed for client in _Client.opened)


def test_every_form_submit_has_its_own_sessions() -> None:
    with pytest.raises(FormNotCompleteError):
        post_form(_generator, {}, [{"node": "node-b"}])
    result = post_form(_generator, {}, [{"node": "node-b"}, {"port": "1"}])

    assert result == {"node": "node-b", "port": "1"}
    assert [client.key for client in _Client.opened] == ["node-a", "node-b", "node-a", "node-b"]
    assert all(client.closed for client in _Client.opened)
