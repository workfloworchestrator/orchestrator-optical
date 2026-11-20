"""Execution test of the shipped configuration override workflow of a Groove G30 node.

The workflow runs through the real orchestrator-core process engine and database, against
a fake NETCONF device driven by the real SDK client: the lines of the form are applied to
the device and recorded in ``optical_applied_config`` under the ``override`` scope of the
node block.
"""

import pytest

pytest.importorskip("g30_4_8_0")

from typing import Any

import g30_4_8_0
from lxml import etree

import orchestrator.core.db as core_db
from orchestrator.optical import db as optical_db
from orchestrator.optical.hal.reconcile import OVERRIDE_SCOPE
from orchestrator.optical.settings import get_settings
from test.support.db import node_instance_id_of_subscription
from test.support.netconf import WRITABLE_RUNNING, FakeManager, install_fake_netconf

pytestmark = pytest.mark.db

GROOVE_G30_PRODUCT = "Nokia Groove G30 Optical Node"
PORT = "/ne:ne/shelf[shelf-id='1']/slot[slot-id='2']/card/port[port-id='1']"


def _config_xml(admin_status: str) -> str:
    return (
        '<ne xmlns="http://coriant.com/yang/os/ne"><shelf><shelf-id>1</shelf-id><slot><slot-id>2</slot-id>'
        f"<card><required-type>CHM2T</required-type><port><port-id>1</port-id><admin-status>{admin_status}"
        "</admin-status></port></card></slot></shelf></ne>"
    )


class _Device(FakeManager):
    """A fake Groove G30 whose port goes down once it receives an edit."""

    def dispatch(self, rpc: Any) -> Any:
        reply = super().dispatch(rpc)
        if etree.QName(rpc).localname == "edit-config":
            self.data_xml = _config_xml("down")
        return reply


@pytest.fixture
def device(monkeypatch: pytest.MonkeyPatch) -> _Device:
    monkeypatch.setenv("OPTICAL_G30_USER", "user")
    monkeypatch.setenv("OPTICAL_G30_PASSWORD", "not-a-real-secret")
    get_settings.cache_clear()
    fake = _Device((WRITABLE_RUNNING,), _config_xml("up"))
    install_fake_netconf(monkeypatch, g30_4_8_0, fake)
    yield fake
    get_settings.cache_clear()


def test_config_override_workflow_applies_and_records_the_overrides(
    seed_optical_node, run_process, assert_process_completed, device: _Device
) -> None:
    subscription_id = seed_optical_node(GROOVE_G30_PRODUCT, "g30-override-01.optical.test", "192.0.2.71")
    node_id = node_instance_id_of_subscription(subscription_id)

    process_id = run_process(
        "modify_optical_node_nokia_groove_g30_config_override",
        [{"subscription_id": subscription_id}, {"configuration_override": f"+ {PORT}/admin-status: down"}, {}],
    )

    assert_process_completed(process_id)
    assert any("<admin-status>down</admin-status>" in xml for name, xml in device.calls if name == "edit-config")
    with core_db.db.database_scope():
        assert optical_db.applied_config(node_id, node_id, OVERRIDE_SCOPE) == {f"{PORT}/admin-status": "down"}
