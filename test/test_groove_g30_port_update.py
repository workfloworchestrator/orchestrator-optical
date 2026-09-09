"""Tests for the Groove G30 port/subport update helper.

The helper exists because the auto-generated ``ItemNode.update()`` validates the payload
against the full ``PortItem``/``SubportItem`` YANG model, whose list key (``port-id`` /
``subport-id``) is a required field. These tests pin that the correct key is injected:
``subport_id`` when the endpoint is a subport, ``port_id`` otherwise.
"""

from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import g30_port_update


class _FakeEndpoint:
    """Record the kwargs passed to ``update`` so the injected list key can be asserted on."""

    def __init__(self) -> None:
        self.calls: dict[str, object] = {}

    def update(self, **kwargs: object) -> None:
        self.calls.update(kwargs)


def test_subport_key_used_when_subport_id_present() -> None:
    endpoint = _FakeEndpoint()
    g30_port_update(endpoint, port_id=5, subport_id=2, admin_status="up")
    assert endpoint.calls == {"subport_id": 2, "admin_status": "up"}


def test_port_key_used_when_subport_id_absent() -> None:
    endpoint = _FakeEndpoint()
    g30_port_update(endpoint, port_id=5, subport_id=None, admin_status="up")
    assert endpoint.calls == {"port_id": 5, "admin_status": "up"}
