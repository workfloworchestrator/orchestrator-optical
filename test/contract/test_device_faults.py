"""Fault-injection contract tests for the device-facing layers.

These tests pin down how the NETCONF (G30/G42) and TL1 (FlexILS) paths behave when a
device misbehaves: unreachable management IPs, ``<rpc-error>`` replies, missing objects
and denied TL1 commands. The NETCONF tests run the real SDK clients against a fake
ncclient manager (see :mod:`test.support.netconf`), so the HAL factories, the SDK
session handling and the adapters are exercised together.
"""

import pytest

pytest.importorskip("flexils_tl1")
pytest.importorskip("g30_4_8_0")
pytest.importorskip("g42_8_0_2")

from types import SimpleNamespace
from typing import Any

import g30_4_8_0
import g42_8_0_2
from flexils_tl1.commands.base import TL1BaseResponse
from flexils_tl1.commands.eqpt import RetrieveEqpt
from flexils_tl1.exceptions import TL1CommandDeniedError
from flexils_tl1.utils import TL1CompletionStatus

from orchestrator.optical.hal.adapters.nokia_groove_g30 import _shared as g30_shared
from orchestrator.optical.hal.adapters.nokia_gx_g42 import _shared as g42_shared
from orchestrator.optical.hal.adapters.nokia_gx_g42 import node as g42_node
from orchestrator.optical.hal.adapters.nokia_gx_g42 import port as g42_port
from orchestrator.optical.hal.adapters.nokia_gx_g42 import transponder as g42_transponder
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
            optical_module_node_fqdn="node.example.net",
            optical_module_node_dcn_loopback_ip=loopback_ip,
            optical_module_node_dcn_interface_ip=interface_ip,
        )
    )


def _port_block(port_name: str) -> Any:
    return SimpleNamespace(optical_port_name=port_name, optical_port_host_node=_node_block())


class _FakeFlexilsClient:
    """Minimal FlexILS client exposing only the raw-command seam used by TL1BaseCommand."""

    def __init__(self, raw_response: str) -> None:
        self.tid = "FLEXILS"
        self._raw_response = raw_response

    def execute_raw_command(self, _command: str, _correlation_tag: str) -> str:
        return self._raw_response


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


def test_g42_edit_is_committed(monkeypatch: pytest.MonkeyPatch) -> None:
    """A G42 HAL write edits the candidate datastore and commits it right away."""
    fake = FakeManager((CANDIDATE,))
    install_fake_netconf(monkeypatch, g42_8_0_2, fake)

    g42_port.set_port_admin_state(_port_block("1-4-L1"), "down")

    names = fake.names()
    edit = next(xml for name, xml in fake.calls if name == "edit-config")
    assert names.index("edit-config") < names.index("commit")
    assert "<candidate/>" in edit
    assert "<admin-state>lock</admin-state>" in edit


def test_g30_edit_targets_running_without_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    """The G30 has no candidate datastore: a HAL write edits running and sends no commit."""
    fake = FakeManager((WRITABLE_RUNNING,))
    install_fake_netconf(monkeypatch, g30_4_8_0, fake)

    client = g30_shared.get_g30_client(_node_block())
    client.data.ne_ne.shelf(1).slot(2).card.port(1).update(port_id=1, admin_status="down")

    edit = next(xml for name, xml in fake.calls if name == "edit-config")
    assert "<running/>" in edit
    assert "commit" not in fake.names()


def test_g42_rpc_error_surfaces_with_its_error_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    """An <rpc-error> on a HAL write is raised as RuntimeError carrying the RFC 6241 error-tag."""
    install_fake_netconf(
        monkeypatch, g42_8_0_2, FakeManager((CANDIDATE,), dispatch_error=rpc_error("operation-failed", "boom"))
    )

    with pytest.raises(RuntimeError, match="boom") as excinfo:
        g42_port.set_port_admin_state(_port_block("1-4-L1"), "up")

    assert getattr(excinfo.value, "rpc_error_tag", None) == "operation-failed"


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
        dst_time_slots="1..20",
    )

    rpc = next(xml for name, xml in fake.calls if name == "create-xcon")
    assert "<source>/ioa-ne:ne/facilities/ethernet[name='1-4-T1']</source>" in rpc
    assert "<dst-parent-odu>x</dst-parent-odu>" in rpc
    assert "<payload-type>100GBE</payload-type>" in rpc
    assert "destination" not in rpc.replace("dst-", "")


def test_g42_missing_object_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A read of an object the device does not have fails loudly instead of returning None."""
    install_fake_netconf(monkeypatch, g42_8_0_2, FakeManager((CANDIDATE,)))

    with pytest.raises(ValueError, match="returned no data"):
        g42_node.software_version(_node_block())


def test_tl1_parse_missing_tag_raises_value_error() -> None:
    """A response without the correlation tag is rejected with a ValueError."""
    with pytest.raises(ValueError, match="Could not find tag WFOTAG"):
        TL1BaseResponse.from_raw_text("M  OTHER COMPLD\n;\n", "WFOTAG")


def test_tl1_parse_missing_status_leaks_attribute_error() -> None:
    """A response whose tag is present but has no status word leaks AttributeError."""
    with pytest.raises(AttributeError, match="NoneType"):
        TL1BaseResponse.from_raw_text("WFOTAG", "WFOTAG")


def test_tl1_parse_unknown_status_raises_value_error() -> None:
    """An unrecognised completion status is rejected by the TL1CompletionStatus enum."""
    raw = "   FLEXILS\nM  WFOTAG BOGUS\n;\nTL1>>"

    with pytest.raises(ValueError, match="BOGUS"):
        TL1BaseResponse.from_raw_text(raw, "WFOTAG")


def test_tl1_denied_command_raises_typed_error() -> None:
    """A DENY response raises TL1CommandDeniedError carrying the tid and the raw response."""
    raw = '   FLEXILS\nM  WFOTAG DENY\n   "AID:TYPE::UP"\n;\nTL1>>'

    with pytest.raises(TL1CommandDeniedError) as excinfo:
        RetrieveEqpt(ctag="WFOTAG").execute(_FakeFlexilsClient(raw))

    assert excinfo.value.tid == "FLEXILS"
    assert "WFOTAG DENY" in excinfo.value.response


def test_tl1_deny_with_already_marker_is_tolerated() -> None:
    """A DENY that also carries ALREADY is parsed, not raised, keeping provisioning idempotent."""
    raw = '   FLEXILS\nM  WFOTAG DENY\n   "AID:TYPE::UP"\n;\n/* ALREADY provisioned */\nTL1>>'

    response = RetrieveEqpt(ctag="WFOTAG").execute(_FakeFlexilsClient(raw))

    assert response.status == TL1CompletionStatus.DENY
