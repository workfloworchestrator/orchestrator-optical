"""A fake ncclient manager, so the real NETCONF SDK clients run without a device.

``install_fake_netconf`` patches ``ncclient.manager.connect`` (as bound by the SDK
session managers) to return a :class:`FakeManager`, which answers ``<get>`` /
``<get-config>`` with canned ``<data>`` XML, records every RPC it receives and can
raise an ``<rpc-error>`` on ``<edit-config>`` or on custom RPCs.
"""

from collections.abc import Callable
from typing import Any

import pytest
from lxml import etree
from ncclient.operations.rpc import RPCError

NC_NS = "urn:ietf:params:xml:ns:netconf:base:1.0"

BASE_CAPABILITIES = ("urn:ietf:params:netconf:base:1.0", "urn:ietf:params:netconf:base:1.1")
CANDIDATE = "urn:ietf:params:netconf:capability:candidate:1.0"
WRITABLE_RUNNING = "urn:ietf:params:netconf:capability:writable-running:1.0"


def rpc_error(tag: str, message: str = "") -> RPCError:
    """Build the ncclient ``RPCError`` for an RFC 6241 ``<rpc-error>`` with ``tag``."""
    raw = etree.fromstring(
        f'<rpc-error xmlns="{NC_NS}"><error-type>application</error-type><error-tag>{tag}</error-tag>'
        f"<error-severity>error</error-severity><error-message>{message}</error-message></rpc-error>"
    )
    return RPCError(raw)


class FakeReply:
    """An ncclient reply: ``ok`` plus the ``<data>`` element of a read."""

    def __init__(self, data_xml: str | None = None) -> None:
        self.ok = True
        self.data_ele = None if data_xml is None else etree.fromstring(f'<data xmlns="{NC_NS}">{data_xml}</data>')


class FakeManager:
    """An ncclient manager answering reads with ``data_xml`` and recording every RPC."""

    def __init__(
        self,
        capabilities: tuple[str, ...],
        data_xml: str = "",
        dispatch_error: RPCError | None = None,
    ) -> None:
        self.server_capabilities = [*BASE_CAPABILITIES, *capabilities]
        self.data_xml = data_xml
        self.dispatch_error = dispatch_error
        self.calls: list[tuple[str, Any]] = []

    def get(self, filter: Any = None, **_: Any) -> FakeReply:  # noqa: A002 - ncclient's keyword
        self.calls.append(("get", filter))
        return FakeReply(self.data_xml)

    def get_config(self, source: str, filter: Any = None, **_: Any) -> FakeReply:  # noqa: A002
        self.calls.append(("get-config", (source, filter)))
        return FakeReply(self.data_xml)

    def dispatch(self, rpc: Any) -> FakeReply:
        self.calls.append((etree.QName(rpc).localname, etree.tostring(rpc, encoding="unicode")))
        if self.dispatch_error is not None:
            raise self.dispatch_error
        return FakeReply()

    def commit(self) -> FakeReply:
        self.calls.append(("commit", None))
        return FakeReply()

    def lock(self, target: str) -> FakeReply:
        self.calls.append(("lock", target))
        return FakeReply()

    def unlock(self, target: str) -> FakeReply:
        self.calls.append(("unlock", target))
        return FakeReply()

    def validate(self, source: str = "candidate") -> FakeReply:
        self.calls.append(("validate", source))
        return FakeReply()

    def discard_changes(self) -> FakeReply:
        self.calls.append(("discard-changes", None))
        return FakeReply()

    def close_session(self) -> None:
        self.calls.append(("close-session", None))

    def names(self) -> list[str]:
        """The names of the RPCs received, in order."""
        return [name for name, _ in self.calls]


def install_fake_netconf(
    monkeypatch: pytest.MonkeyPatch,
    sdk_module: Any,
    manager: FakeManager | Callable[..., FakeManager],
) -> list[dict[str, Any]]:
    """Make ``sdk_module.session_manager`` connect to ``manager``; return the connect kwargs seen.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        sdk_module: The SDK package (e.g. ``g42_8_0_2``).
        manager: The manager to return, or a factory called with the connect kwargs
            (raise from it to simulate an unreachable host).

    Returns:
        The list the keyword arguments of each connection attempt are appended to.
    """
    attempts: list[dict[str, Any]] = []

    def connect(**kwargs: Any) -> FakeManager:
        attempts.append(kwargs)
        return manager(**kwargs) if callable(manager) else manager

    monkeypatch.setattr(sdk_module.session_manager.manager, "connect", connect)
    return attempts
