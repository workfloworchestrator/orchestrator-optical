"""Unit tests for TLS/SSH verification wiring of the Nokia device clients.

TLS verification is secure by default (``True``): labs opt out explicitly with
``OPTICAL_*_VERIFY=false``, and private-PKI production networks point the setting
at a CA bundle file. The FlexILS SSH client follows the SSH-analogous semantics
(reject unknown host keys by default, ``false`` auto-accepts them for labs, or a
known-hosts file path). No device is contacted.
"""

from typing import ClassVar

import pytest

from orchestrator.optical.services.nokia.flexils.client import FlexilsClient
from orchestrator.optical.services.nokia.g30.session_manager import RestconfClient as G30RestconfClient
from orchestrator.optical.services.nokia.g42.session_manager import RestconfClient as G42RestconfClient
from orchestrator.optical.services.nokia.tnms.client import TnmsClient
from orchestrator.optical.settings import get_settings

pytestmark = pytest.mark.unit

_AUTH_VALUE = "not-a-real-secret"

_G30_ENV = {
    "OPTICAL_G30_USER": "user",
    "OPTICAL_G30_PASSWORD": "password",
}
_G42_ENV = {
    "OPTICAL_G42_USER": "user",
    "OPTICAL_G42_PASSWORD": "password",
}
_TNMS_ENV = {
    "OPTICAL_TNMS_USER": "user",
    "OPTICAL_TNMS_PASSWORD": "password",
    "OPTICAL_TNMS_ENDPOINT": "https://tnms.example.com",
}


@pytest.fixture(autouse=True)
def _clear_caches():
    get_settings.cache_clear()
    FlexilsClient.close_all()
    yield
    get_settings.cache_clear()
    FlexilsClient.close_all()


def test_g30_verifies_tls_by_default(monkeypatch) -> None:
    for key, value in _G30_ENV.items():
        monkeypatch.setenv(key, value)
    for var in ("OPTICAL_G30_VERIFY",):
        monkeypatch.delenv(var, raising=False)

    client = G30RestconfClient(management_ip="10.0.0.1")

    assert client._session.verify is True  # noqa: SLF001
    assert client._session.trust_env is True  # noqa: SLF001


def test_g30_explicit_verify_overrides_settings(monkeypatch) -> None:
    for key, value in _G30_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("OPTICAL_G30_VERIFY", "false")

    disabled = G30RestconfClient(management_ip="10.0.0.1")
    assert disabled._session.verify is False  # noqa: SLF001
    assert disabled._session.trust_env is False  # noqa: SLF001

    explicit = G30RestconfClient(management_ip="10.0.0.1", verify=True)
    assert explicit._session.verify is True  # noqa: SLF001

    bundle = G30RestconfClient(management_ip="10.0.0.1", verify="/etc/ssl/g30-ca.pem")
    assert bundle._session.verify == "/etc/ssl/g30-ca.pem"  # noqa: SLF001
    assert bundle._session.trust_env is True  # noqa: SLF001


def test_g42_verifies_tls_by_default() -> None:
    client = G42RestconfClient(management_ip="10.0.0.1", username="user", password=_AUTH_VALUE)

    assert client._session.verify is True  # noqa: SLF001
    assert client._session.trust_env is True  # noqa: SLF001


def test_g42_verify_flows_from_settings_and_explicit_arg(monkeypatch) -> None:
    monkeypatch.setenv("OPTICAL_G42_VERIFY", "false")

    from_settings = G42RestconfClient(management_ip="10.0.0.1", username="user", password=_AUTH_VALUE)
    assert from_settings._session.verify is False  # noqa: SLF001

    explicit = G42RestconfClient(management_ip="10.0.0.1", username="user", password=_AUTH_VALUE, verify=True)
    assert explicit._session.verify is True  # noqa: SLF001


def test_tnms_verifies_tls_by_default() -> None:
    client = TnmsClient("user", "password", "https://tnms.example.com")

    assert client._session.verify is True  # noqa: SLF001
    assert client._session.trust_env is True  # noqa: SLF001


def test_tnms_from_settings_threads_verify(monkeypatch) -> None:
    for key, value in _TNMS_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("OPTICAL_TNMS_VERIFY", "false")

    assert TnmsClient.from_settings()._session.verify is False  # noqa: SLF001

    monkeypatch.setenv("OPTICAL_TNMS_VERIFY", "/etc/ssl/tnms-ca.pem")
    get_settings.cache_clear()

    assert TnmsClient.from_settings()._session.verify == "/etc/ssl/tnms-ca.pem"  # noqa: SLF001


def test_flexils_verifies_host_key_by_default() -> None:
    client = FlexilsClient(tid="FLEXILS", gne_ip="10.0.0.1")

    assert client._verify_host_key is True  # noqa: SLF001


def test_flexils_explicit_verify_overrides_settings(monkeypatch) -> None:
    monkeypatch.setenv("OPTICAL_FLEXILS_VERIFY_HOST_KEY", "false")

    assert FlexilsClient(tid="FLEXILS", gne_ip="10.0.0.1")._verify_host_key is False  # noqa: SLF001
    client = FlexilsClient(tid="FLEXILS", gne_ip="10.0.0.1", verify_host_key="/root/.ssh/known_hosts")
    assert client._verify_host_key == "/root/.ssh/known_hosts"  # noqa: SLF001


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
