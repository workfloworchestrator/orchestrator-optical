"""Unit tests for the TLS/SSH verification wiring of the Nokia device clients.

Verification is secure by default. The G30/G42 NETCONF sessions verify the SSH host
key unless ``OPTICAL_*_VERIFY=false`` (lab use only); the FlexILS SSH client rejects
unknown host keys by default, ``false`` auto-accepts them, or it verifies against a
known-hosts file path. The device clients take credentials and the verification
policy as explicit arguments; the ``hal`` client factories read them from the
settings. No device is contacted.
"""

import pytest

pytest.importorskip("flexils_tl1")
pytest.importorskip("g30_4_8_0")
pytest.importorskip("g42_8_0_2")

from types import SimpleNamespace
from typing import Any, ClassVar

import g30_4_8_0
import g42_8_0_2
from flexils_tl1.client import FlexilsClient

from orchestrator.optical.hal.adapters.nokia_flexils._shared import _flexils_client
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import get_g30_client
from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import get_g42_client
from orchestrator.optical.settings import get_settings
from test.support.netconf import WRITABLE_RUNNING, FakeManager, install_fake_netconf

pytestmark = pytest.mark.unit

_AUTH_VALUE = "not-a-real-secret"

_NETCONF_FACTORIES = [
    pytest.param(get_g30_client, g30_4_8_0, "G30", id="g30"),
    pytest.param(get_g42_client, g42_8_0_2, "G42", id="g42"),
]


def _node_block() -> Any:
    """Duck-typed node block exposing only the management fields read by the client factories."""
    return SimpleNamespace(
        management=SimpleNamespace(
            optical_module_node_fqdn="node.example.net",
            optical_module_node_dcn_loopback_ip=None,
            optical_module_node_dcn_interface_ip="10.0.0.1",
        )
    )


@pytest.fixture(autouse=True)
def _clear_caches():
    get_settings.cache_clear()
    FlexilsClient.close_all()
    yield
    get_settings.cache_clear()
    FlexilsClient.close_all()


@pytest.mark.parametrize(("factory", "sdk", "prefix"), _NETCONF_FACTORIES)
def test_netconf_factory_threads_settings(factory, sdk, prefix: str, monkeypatch) -> None:
    attempts = install_fake_netconf(monkeypatch, sdk, FakeManager((WRITABLE_RUNNING,)))
    monkeypatch.setenv(f"OPTICAL_{prefix}_USER", "alice")
    monkeypatch.setenv(f"OPTICAL_{prefix}_PASSWORD", _AUTH_VALUE)
    monkeypatch.delenv(f"OPTICAL_{prefix}_VERIFY", raising=False)

    client = factory(_node_block())

    assert client.auto_commit is True
    assert attempts[-1]["host"] == "10.0.0.1"
    assert attempts[-1]["port"] == 830
    assert attempts[-1]["username"] == "alice"
    assert attempts[-1]["password"] == _AUTH_VALUE
    assert attempts[-1]["hostkey_verify"] is True

    monkeypatch.setenv(f"OPTICAL_{prefix}_VERIFY", "false")
    get_settings.cache_clear()
    factory(_node_block())
    assert attempts[-1]["hostkey_verify"] is False


@pytest.mark.parametrize("prefix", ["G30", "G42"])
def test_netconf_verify_rejects_a_trust_store_path(prefix: str, monkeypatch) -> None:
    monkeypatch.setenv(f"OPTICAL_{prefix}_VERIFY", "/etc/ssl/ca.pem")

    with pytest.raises(ValueError, match="takes no file path"):
        get_settings()


def test_flexils_verifies_host_key_by_default() -> None:
    client = FlexilsClient(tid="FLEXILS", gne_ip="10.0.0.1")

    assert client._verify_host_key is True  # noqa: SLF001


def test_flexils_explicit_verify() -> None:
    assert FlexilsClient(tid="FLEXILS", gne_ip="10.0.0.1", verify_host_key=False)._verify_host_key is False  # noqa: SLF001
    client = FlexilsClient(tid="FLEXILS", gne_ip="10.0.0.1", verify_host_key="/root/.ssh/known_hosts")
    assert client._verify_host_key == "/root/.ssh/known_hosts"  # noqa: SLF001


def test_flexils_factory_threads_settings(monkeypatch) -> None:
    monkeypatch.setenv("OPTICAL_FLEXILS_USER", "alice")
    monkeypatch.setenv("OPTICAL_FLEXILS_PASSWORD", _AUTH_VALUE)
    monkeypatch.setenv("OPTICAL_FLEXILS_VERIFY_HOST_KEY", "/root/.ssh/known_hosts")

    client = _flexils_client("FLEXILS", "10.0.0.1")

    assert client._username == "alice"  # noqa: SLF001
    assert client._password == _AUTH_VALUE  # noqa: SLF001
    assert client._verify_host_key == "/root/.ssh/known_hosts"  # noqa: SLF001
    assert _flexils_client("FLEXILS", "10.0.0.1") is client


def test_flexils_cache_key_distinguishes_verify_policies() -> None:
    default = FlexilsClient.get_instance(tid="FLEXILS", gne_ip="10.0.0.1")
    assert FlexilsClient.get_instance(tid="FLEXILS", gne_ip="10.0.0.1") is default

    lab = FlexilsClient.get_instance(tid="FLEXILS", gne_ip="10.0.0.1", verify_host_key=False)
    assert lab is not default
    assert lab._verify_host_key is False  # noqa: SLF001


class _FakeSSHClient:
    """Fake paramiko client recording the host-key policy; connect stops before any socket."""

    instances: ClassVar[list["_FakeSSHClient"]] = []

    def __init__(self) -> None:
        self.policies: list = []
        self.loaded_system = 0
        self.loaded_paths: list[str] = []
        _FakeSSHClient.instances.append(self)

    def set_missing_host_key_policy(self, policy) -> None:
        self.policies.append(policy)

    def load_system_host_keys(self, _filename=None) -> None:
        self.loaded_system += 1

    def load_host_keys(self, filename: str) -> None:
        self.loaded_paths.append(filename)

    def connect(self, **_kwargs) -> None:
        raise RuntimeError

    def close(self) -> None:
        pass


def _connect_policy(client: FlexilsClient, monkeypatch: pytest.MonkeyPatch):
    import paramiko

    _FakeSSHClient.instances.clear()
    monkeypatch.setattr(paramiko, "SSHClient", _FakeSSHClient)
    with pytest.raises(RuntimeError):
        client._connect()  # noqa: SLF001
    assert len(_FakeSSHClient.instances) == 1
    return _FakeSSHClient.instances[0]


def test_flexils_rejects_unknown_host_keys_by_default(monkeypatch) -> None:
    import paramiko

    client = FlexilsClient(tid="FLEXILS", gne_ip="10.0.0.1", username="user", password=_AUTH_VALUE)
    fake = _connect_policy(client, monkeypatch)

    assert fake.loaded_system == 1
    assert fake.loaded_paths == []
    assert len(fake.policies) == 1
    assert isinstance(fake.policies[0], paramiko.RejectPolicy)


def test_flexils_lab_mode_auto_adds_host_keys(monkeypatch) -> None:
    import paramiko

    fake = _connect_policy(
        FlexilsClient(tid="FLEXILS", gne_ip="10.0.0.1", username="user", password=_AUTH_VALUE, verify_host_key=False),
        monkeypatch,
    )

    assert fake.loaded_system == 0
    assert len(fake.policies) == 1
    assert isinstance(fake.policies[0], paramiko.AutoAddPolicy)


def test_flexils_loads_custom_known_hosts_file(monkeypatch) -> None:
    import paramiko

    fake = _connect_policy(
        FlexilsClient(
            tid="FLEXILS",
            gne_ip="10.0.0.1",
            username="user",
            password=_AUTH_VALUE,
            verify_host_key="/root/.ssh/known_hosts",
        ),
        monkeypatch,
    )

    assert fake.loaded_system == 1
    assert fake.loaded_paths == ["/root/.ssh/known_hosts"]
    assert len(fake.policies) == 1
    assert isinstance(fake.policies[0], paramiko.RejectPolicy)
