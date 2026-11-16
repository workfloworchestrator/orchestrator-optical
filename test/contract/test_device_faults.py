"""Fault-injection contract tests for the device-facing layers.

These tests pin down how the NETCONF (G30/G42) paths behave when a device misbehaves:
unreachable management IPs, ``<rpc-error>`` replies and missing objects. They run the
real SDK clients against a fake ncclient manager (see :mod:`test.support.netconf`), so
the HAL factories, the SDK session handling and the adapters are exercised together.
The TL1 (FlexILS) denials are covered in :mod:`test.contract.test_flexils_tl1`.
"""

import pytest

pytest.importorskip("g30_4_8_0")
pytest.importorskip("g42_8_0_2")

from types import SimpleNamespace
from typing import Any

import g30_4_8_0
import g42_8_0_2

from orchestrator.optical.hal.adapters.nokia_groove_g30 import _shared as g30_shared
from orchestrator.optical.hal.adapters.nokia_gx_g42 import _shared as g42_shared
from orchestrator.optical.hal.adapters.nokia_gx_g42 import node as g42_node
from orchestrator.optical.hal.adapters.nokia_gx_g42 import transponder as g42_transponder
from orchestrator.optical.hal.sessions import close_idle_device_sessions, device_sessions
from orchestrator.optical.settings import get_settings
from test.support.netconf import CANDIDATE, WRITABLE_RUNNING, FakeManager, install_fake_netconf, rpc_error

pytestmark = pytest.mark.contract

_AUTH_VALUE = "not-a-real-secret"


@pytest.fixture(autouse=True)
def _credentials(monkeypatch: pytest.MonkeyPatch):
    for prefix in ("G30", "G42"):
        monkeypatch.setenv(f"OPTICAL_{prefix}_USER", "user")
        monkeypatch.setenv(f"OPTICAL_{prefix}_PASSWORD", _AUTH_VALUE)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _node_block(loopback_ip: str | None = "10.0.0.1", interface_ip: str | None = "10.0.0.2") -> Any:
    return SimpleNamespace(
        management=SimpleNamespace(
            optical_module_node_name="node.example.net",
            optical_module_node_management_loopback_ip=loopback_ip,
            optical_module_node_management_ip=interface_ip,
        )
    )


def _port_block(port_name: str) -> Any:
    return SimpleNamespace(optical_port_name=port_name, optical_port_host_node=_node_block())


def test_netconf_factory_falls_back_to_the_interface_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unreachable loopback IP is skipped: the session is opened on the DCN interface IP."""
    fake = FakeManager((WRITABLE_RUNNING,))

    def connect(**kwargs: Any) -> FakeManager:
        if kwargs["host"] == "10.0.0.1":
            msg = "no route to host"
            raise OSError(msg)
        return fake

    attempts = install_fake_netconf(monkeypatch, g30_4_8_0, connect)

    client = g30_shared.get_g30_client(_node_block())

    assert [a["host"] for a in attempts] == ["10.0.0.1", "10.0.0.2"]
    assert client.host == "10.0.0.2"
    assert attempts[-1]["username"] == "user"
    assert attempts[-1]["hostkey_verify"] is True


def test_netconf_factory_authenticates_by_password_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """The SSH agent and the local keys are not offered before the password."""
    attempts = install_fake_netconf(monkeypatch, g42_8_0_2, FakeManager((CANDIDATE,)))

    g42_shared.get_g42_client(_node_block())

    assert attempts[-1]["allow_agent"] is False
    assert attempts[-1]["look_for_keys"] is False


def test_netconf_factory_shares_one_session_per_node_within_a_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    """A node is logged into once: within a scope, and by the next scope, until the idle sessions are closed."""
    fake = FakeManager((WRITABLE_RUNNING,))
    attempts = install_fake_netconf(monkeypatch, g30_4_8_0, fake)

    with device_sessions():
        first = g30_shared.get_g30_client(_node_block())
        second = g30_shared.get_g30_client(_node_block())
        other_node = g30_shared.get_g30_client(_node_block("10.0.1.1", "10.0.1.2"))
        assert "close-session" not in fake.names()

    with device_sessions():
        assert g30_shared.get_g30_client(_node_block()) is first

    assert first is second
    assert other_node is not first
    assert [a["host"] for a in attempts] == ["10.0.0.1", "10.0.1.1"]
    assert "close-session" not in fake.names()
    close_idle_device_sessions()
    assert fake.names().count("close-session") == 2


def test_netconf_factory_opens_a_session_per_call_outside_a_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without a scope every call is its own session (the behaviour of code not opting in)."""
    attempts = install_fake_netconf(monkeypatch, g30_4_8_0, FakeManager((WRITABLE_RUNNING,)))

    assert g30_shared.get_g30_client(_node_block()) is not g30_shared.get_g30_client(_node_block())
    assert len(attempts) == 2


def test_netconf_factory_reports_every_failed_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    """When no management IP is reachable the factory raises one exception per attempt."""

    def connect(**kwargs: Any) -> FakeManager:
        msg = f"unreachable {kwargs['host']}"
        raise OSError(msg)

    install_fake_netconf(monkeypatch, g42_8_0_2, connect)

    with pytest.raises(ExceptionGroup, match="node.example.net") as excinfo:
        g42_shared.get_g42_client(_node_block())

    assert len(excinfo.value.exceptions) == 2


def test_netconf_factory_requires_a_management_ip() -> None:
    """A node without management IPs is rejected before any connection attempt."""
    with pytest.raises(ValueError, match="no management IP"):
        g42_shared.get_g42_client(_node_block(loopback_ip=None, interface_ip=None))


def test_g30_edit_targets_running_without_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    """The G30 has no candidate datastore: a HAL write edits running and sends no commit."""
    fake = FakeManager((WRITABLE_RUNNING,))
    install_fake_netconf(monkeypatch, g30_4_8_0, fake)

    client = g30_shared.get_g30_client(_node_block())
    client.data.ne_ne.shelf(1).slot(2).card.port(1).update(port_id=1, admin_status="down")

    edit = next(xml for name, xml in fake.calls if name == "edit-config")
    assert "<running/>" in edit
    assert "commit" not in fake.names()


def test_g42_create_existing_xcon_is_tolerated(monkeypatch: pytest.MonkeyPatch) -> None:
    """A create-xcon answered with data-exists keeps provisioning idempotent."""
    fake = FakeManager((CANDIDATE,), dispatch_error=rpc_error("data-exists"))
    install_fake_netconf(monkeypatch, g42_8_0_2, fake)
    g42 = g42_shared.get_g42_client(_node_block())

    g42_transponder._create_xcon(  # noqa: SLF001
        g42,
        client="/ioa-ne:ne/facilities/ethernet[name='1-4-T1']",
        dst_parent_odu="x",
        direction="two-way",
        payload_type="100GBE",
        label="label",
        circuit_identifier="cid",
        dst_time_slots="1..20",
    )

    rpc = next(xml for name, xml in fake.calls if name == "create-xcon")
    # The SDK qualifies every step of an instance-identifier on the wire.
    assert "<source>/ioa-ne:ne/ioa-ne:facilities/ioa-ne:ethernet[ioa-ne:name='1-4-T1']</source>" in rpc
    assert "<dst-parent-odu>x</dst-parent-odu>" in rpc
    assert "<payload-type>100GBE</payload-type>" in rpc
    assert "<circuit-id-suffix>cid</circuit-id-suffix>" in rpc
    assert "destination" not in rpc.replace("dst-", "")


def test_g42_missing_object_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A read of an object the device does not have fails loudly instead of returning None."""
    install_fake_netconf(monkeypatch, g42_8_0_2, FakeManager((CANDIDATE,)))

    with pytest.raises(ValueError, match="returned no data"):
        g42_node.software_version(_node_block())
