"""Tests for the device reads remembered across the submits of a form (never by workflow steps)."""

from uuid import uuid4

import pytest
from pydantic import field_validator
from pydantic_forms.core import FormPage, post_form
from pydantic_forms.exceptions import FormNotCompleteError, FormValidationError
from pydantic_forms.types import FormGenerator, State

from orchestrator.optical.hal import read_cache as read_cache_module
from orchestrator.optical.hal.read_cache import DeviceReads, cached_device_read
from orchestrator.optical.hal.sessions import device_sessions
from orchestrator.optical.products.product_blocks.optical_location import OpticalModuleLocationBlockInactive
from orchestrator.optical.settings import get_settings
from orchestrator.optical.workflows.shared import retryable_form

pytestmark = pytest.mark.unit

READS: list[tuple] = []
DEVICE = {"ports": ["1", "2"], "down": False}


@cached_device_read
def _ports(node: str, roles: list[str] | None = None) -> list[str]:
    if DEVICE["down"]:
        msg = "device unreachable"
        raise ConnectionError(msg)
    READS.append((node, roles))
    return list(DEVICE["ports"])


@pytest.fixture(autouse=True)
def _reset() -> None:
    READS.clear()
    DEVICE.update(ports=["1", "2"], down=False)


def test_outside_a_form_submit_every_call_reads_the_device() -> None:
    _ports("node-a")
    with device_sessions():  # a workflow step
        _ports("node-a")
    assert len(READS) == 2


def test_a_read_is_remembered_by_the_following_submits() -> None:
    with DeviceReads().active():
        assert _ports("node-a") == ["1", "2"]
        assert _ports("node-a") == ["1", "2"]
    DEVICE["ports"] = ["3"]
    with DeviceReads().active():
        assert _ports("node-a") == ["1", "2"]
    assert len(READS) == 1


def test_the_arguments_tell_the_reads_apart_however_they_are_passed() -> None:
    with DeviceReads().active():
        _ports("node-a")
        _ports("node-a", None)
        _ports(node="node-a", roles=None)
        _ports("node-b")
        _ports("node-a", ["line"])
        _ports("node-a", roles=["line"])
    assert READS == [("node-a", None), ("node-b", None), ("node-a", ["line"])]


def test_a_block_argument_counts_as_its_instance() -> None:
    @cached_device_read
    def read(block: OpticalModuleLocationBlockInactive) -> str:
        READS.append((block.subscription_instance_id,))
        return "x"

    one = OpticalModuleLocationBlockInactive.model_construct(subscription_instance_id=uuid4())
    same = OpticalModuleLocationBlockInactive.model_construct(subscription_instance_id=one.subscription_instance_id)
    other = OpticalModuleLocationBlockInactive.model_construct(subscription_instance_id=uuid4())
    with DeviceReads().active():
        read(one)
        read(same)
        read(other)
    assert len(READS) == 2


def test_a_caller_changing_a_result_does_not_change_what_is_remembered() -> None:
    with DeviceReads().active():
        _ports("node-a").append("mine")
        _ports("node-a").append("mine")
        assert _ports("node-a") == ["1", "2"]


def test_a_result_expires_counted_from_the_read(monkeypatch: pytest.MonkeyPatch) -> None:
    now = [0.0]
    monkeypatch.setattr(read_cache_module.time, "monotonic", lambda: now[0])
    with DeviceReads().active():
        _ports("node-a")
        now[0] = get_settings().device_read_cache_seconds - 1
        _ports("node-a")  # a hit does not extend it
        assert len(READS) == 1
        now[0] += 1
        _ports("node-a")
    assert len(READS) == 2


def test_nothing_is_remembered_when_the_time_is_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "device_read_cache_seconds", 0)
    with DeviceReads().active():
        _ports("node-a")
        _ports("node-a")
    assert len(READS) == 2


def test_errors_are_not_remembered() -> None:
    DEVICE["down"] = True
    with DeviceReads().active():
        with pytest.raises(ConnectionError):
            _ports("node-a")
        DEVICE["down"] = False
        assert _ports("node-a") == ["1", "2"]


def test_forget_drops_what_the_scope_read_or_reused_and_nothing_else() -> None:
    with DeviceReads().active():
        _ports("node-a")
        _ports("node-b")
    reads = DeviceReads()
    with reads.active():
        _ports("node-a")  # reused
    reads.forget()
    with DeviceReads().active():
        _ports("node-a")
        _ports("node-b")
    assert [node for node, _ in READS] == ["node-a", "node-b", "node-a"]


class NodePage(FormPage):
    node: str


class PortPage(FormPage):
    port: str

    @field_validator("port")
    @classmethod
    def _exists(cls, value: str) -> str:
        if value not in _ports("node-a"):
            msg = f"no port {value}"
            raise ValueError(msg)
        return value


class LastPage(FormPage):
    note: str


@retryable_form
def _form() -> FormGenerator:
    node = yield NodePage
    _ports(node.node)
    port = yield PortPage
    last = yield LastPage
    return {**node.model_dump(), **port.model_dump(), **last.model_dump()}


def _generator(_state: State) -> FormGenerator:
    return (yield from _form())


def test_a_form_reads_the_device_once_over_its_submits() -> None:
    pages = [{"node": "node-a"}, {"port": "1"}, {"note": "n"}]
    for submitted in (1, 2):
        with pytest.raises(FormNotCompleteError):
            post_form(_generator, {}, pages[:submitted])
    assert post_form(_generator, {}, pages) == {"node": "node-a", "port": "1", "note": "n"}
    assert len(READS) == 1


def test_a_rejected_submit_makes_the_next_one_read_the_device_again() -> None:
    pages = [{"node": "node-a"}, {"port": "3"}]
    with pytest.raises(FormValidationError):
        post_form(_generator, {}, pages)
    DEVICE["ports"] = ["1", "2", "3"]  # the cause is fixed on the device
    with pytest.raises(FormNotCompleteError):
        post_form(_generator, {}, pages)
    assert len(READS) == 2
