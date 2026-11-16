"""Contract tests for the declarative configuration of the NETCONF devices.

The Groove G30 and GX G42 adapters render the desired configuration and hand it to
:mod:`orchestrator.optical.hal.reconcile`. These tests run the real SDK clients against a
fake ncclient manager (see :mod:`test.support.netconf`) and an in-memory applied-configuration
store, so rendering, the SDK diff, the edit sent to the device and the recorded
configuration are exercised together.
"""

import pytest

pytest.importorskip("g30_4_8_0")
pytest.importorskip("g42_8_0_2")

from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import g30_4_8_0
import g42_8_0_2
from g30_4_8_0.data_navigators import Data as G30Data
from g42_8_0_2.data_navigators import Data as G42Data
from lxml import etree

from orchestrator.optical.hal import reconcile
from orchestrator.optical.hal.adapters.nokia_groove_g30 import config as g30_config
from orchestrator.optical.hal.adapters.nokia_groove_g30 import node as g30_node
from orchestrator.optical.hal.adapters.nokia_groove_g30 import port as g30_port
from orchestrator.optical.hal.adapters.nokia_groove_g30 import transponder as g30_transponder
from orchestrator.optical.hal.adapters.nokia_gx_g42 import config as g42_config
from orchestrator.optical.hal.adapters.nokia_gx_g42 import port as g42_port
from orchestrator.optical.hal.adapters.nokia_gx_g42 import transponder as g42_transponder
from orchestrator.optical.hal.reconcile import (
    ConfigApplyError,
    ConfigConflictError,
    ConfigDriftError,
    DeleteEntry,
    Reset,
    fragment,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed
from orchestrator.optical.settings import get_settings
from test.support.applied_config import AppliedConfigStore
from test.support.netconf import CANDIDATE, WRITABLE_RUNNING, FakeManager, install_fake_netconf, rpc_error

pytestmark = pytest.mark.contract

G30_PORT = "/ne:ne/shelf[shelf-id='1']/slot[slot-id='2']/card/port[port-id='1']"
G42_PORT = "/ioa-network-element:ne/equipment/card[name='1-4']/port[name='L1']"


@pytest.fixture(autouse=True)
def _credentials(monkeypatch: pytest.MonkeyPatch):
    for prefix in ("G30", "G42"):
        monkeypatch.setenv(f"OPTICAL_{prefix}_USER", "user")
        monkeypatch.setenv(f"OPTICAL_{prefix}_PASSWORD", "not-a-real-secret")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class _Device(FakeManager):
    """A fake device whose configuration becomes ``after_xml`` once it receives an edit."""

    def __init__(self, capabilities: tuple[str, ...], data_xml: str = "", after_xml: str | None = None, **kwargs: Any):
        super().__init__(capabilities, data_xml, **kwargs)
        self.after_xml = after_xml

    def dispatch(self, rpc: Any) -> Any:
        reply = super().dispatch(rpc)
        if etree.QName(rpc).localname == "edit-config" and self.after_xml is not None:
            self.data_xml = self.after_xml
        return reply

    def edits(self) -> list[str]:
        return [xml for name, xml in self.calls if name == "edit-config"]


def _g30_port_xml(**leaves: str) -> str:
    body = "".join(f"<{name}>{value}</{name}>" for name, value in leaves.items())
    return (
        '<ne xmlns="http://coriant.com/yang/os/ne"><shelf><shelf-id>1</shelf-id><slot><slot-id>2</slot-id>'
        f"<card><port><port-id>1</port-id>{body}</port></card></slot></shelf></ne>"
    )


def _g42_port_xml(**leaves: str) -> str:
    body = "".join(f"<{name}>{value}</{name}>" for name, value in leaves.items())
    return (
        '<ne xmlns="http://infinera.com/yang/ioa/ne"><equipment><card><name>1-4</name>'
        f"<port><name>L1</name>{body}</port></card></equipment></ne>"
    )


def _node(platform: Platform, fqdn: str = "node.example.net") -> Any:
    return SimpleNamespace(
        subscription_instance_id=uuid4(),
        management=SimpleNamespace(
            optical_module_node_name=fqdn,
            optical_module_node_vendor=Vendor.NOKIA,
            optical_module_node_platform=platform,
            optical_module_node_management_loopback_ip="10.0.0.1",
            optical_module_node_management_ip=None,
        ),
    )


def _port(
    port_name: str,
    host_node: Any,
    role: OpticalPortRole = OpticalPortRole.TRANSPONDER_LINE,
) -> Any:
    return SimpleNamespace(
        subscription_instance_id=uuid4(),
        optical_port_name=port_name,
        optical_port_host_node=host_node,
        optical_port_role=role,
    )


def _g30(monkeypatch: pytest.MonkeyPatch, data_xml: str, after_xml: str | None = None) -> _Device:
    device = _Device((WRITABLE_RUNNING,), data_xml, after_xml)
    install_fake_netconf(monkeypatch, g30_4_8_0, device)
    return device


def _g42(monkeypatch: pytest.MonkeyPatch, data_xml: str, after_xml: str | None = None, **kwargs: Any) -> _Device:
    device = _Device((CANDIDATE,), data_xml, after_xml, **kwargs)
    install_fake_netconf(monkeypatch, g42_8_0_2, device)
    return device


# ---------------------------------------------------------------------------
# Rendering (no device)
# ---------------------------------------------------------------------------


def test_fragment_flattens_the_given_leaves_without_the_entry_keys() -> None:
    port = G30Data(None).ne_ne.shelf(1).slot(2).card.port(1)

    rendered = fragment(port, port_id=1, admin_status="up", service_label="svc")

    assert rendered.leaves == {f"{G30_PORT}/admin-status": "up", f"{G30_PORT}/service-label": "svc"}


def test_fragment_validates_each_leaf_with_the_sdk_model() -> None:
    port = G30Data(None).ne_ne.shelf(1).slot(2).card.port(1)

    with pytest.raises(ValueError, match="admin_status"):
        fragment(port, admin_status="sideways")


def test_fragment_needs_no_mandatory_leaf_of_the_node() -> None:
    och_os = G30Data(None).ne_ne.shelf(1).slot(2).card.port(1).och_os

    rendered = fragment(och_os, required_tx_optical_power=Decimal("1.50"))

    assert rendered.leaves == {f"{G30_PORT}/och-os/required-tx-optical-power": "1.50"}


def test_g30_line_rendering_puts_the_optical_channel_one_stage_after_its_port() -> None:
    fragments = g30_transponder.render_line_transceivers(
        G30Data(None), ("port-1/2/1",), (193_100_000,), ("QPSK_100G",), ("spectrum-a",)
    )

    port, och_os = fragments
    assert (port.stage, och_os.stage) == (0, 1)
    assert port.leaves == {
        f"{G30_PORT}/port-mode": "QPSK_100G",
        f"{G30_PORT}/admin-status": "up",
        f"{G30_PORT}/service-label": "spectrum-a",
    }
    assert och_os.leaves[f"{G30_PORT}/och-os/frequency"] == 193_100_000
    assert och_os.leaves[f"{G30_PORT}/och-os/modulation-format"] == "DP-QPSK"
    assert och_os.leaves[f"{G30_PORT}/och-os/rate-class"] == "100G"


def test_g30_client_rendering_follows_the_service_speed() -> None:
    port, ethernet = g30_transponder.render_transceiver_client(
        G30Data(None),
        "port-1/2/1",
        "svc",
        OpticalDigitalServiceSpeed._400,  # noqa: SLF001
    )

    assert port.leaves[f"{G30_PORT}/port-mode"] == "400GBE"
    assert ethernet.stage == 1
    assert ethernet.leaves[f"{G30_PORT}/eth400g/eth-fec-type"] == "enabled"


def test_g42_line_rendering_covers_ports_groups_super_channel_and_carriers() -> None:
    fragments = g42_transponder.render_line_transceivers(
        G42Data(None),
        ("1-4-L1", "1-4-L2"),
        (193_100_000, 193_200_000),
        ("mode", "mode"),
        ("ch-01 > g30.a 1/1/L1", "ch-02 > g30.a 1/1/L2"),
    )

    leaves = {path: value for item in fragments for path, value in item.leaves.items()}
    super_channel = "/ioa-network-element:ne/facilities/super-channel[name='1-4-L1_1-4-L2']"
    assert leaves[f"{G42_PORT}/admin-state"] == "unlock"
    assert leaves[f"{G42_PORT}/label"] == "ch-01 > g30.a 1/1/L1"
    assert leaves[f"{super_channel}/label"] == "ch-01 + ch-02"
    assert leaves[f"{super_channel}/carriers[.='1-4-L2-1']"] == "1-4-L2-1"
    assert [item.stage for item in fragments] == [0, 0, 0, 0, 0, 1, 1]


def test_g42_line_rendering_rejects_mixed_modes() -> None:
    with pytest.raises(ValueError, match="All modes must be the same"):
        g42_transponder.render_line_transceivers(G42Data(None), ("1-4-L1", "1-4-L2"), (1, 2), ("a", "b"), ("a", "b"))


# ---------------------------------------------------------------------------
# Release rules
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (f"{G30_PORT}/admin-status", Reset("down")),
        (f"{G30_PORT}/port-mode", Reset("not-applicable")),
        (f"{G30_PORT}/connected-to", Reset("")),
        (f"{G30_PORT}/och-os/frequency", None),
        (f"{G30_PORT}/eth100g/admin-status", None),
        (
            "/ne:ne/shelf[shelf-id='1']/slot[slot-id='3']/card/subslot[subslot-id='1']/subcard/port[port-id='1']/admin-status",
            None,
        ),
        (
            "/ne:ne/shelf[shelf-id='1']/slot[slot-id='3']/card/subslot[subslot-id='1']/subcard/port[port-id='1']/connected-to",
            Reset(""),
        ),
        (
            "/ne:ne/shelf[shelf-id='1']/slot[slot-id='3']/card/subslot[subslot-id='2']/subcard/amplifier[amplifier-name='ba']/target-gain",
            None,
        ),
        (
            """/ne:ne/services/CRS[src-tp="/ne:ne/shelf[shelf-id='1']/x"][dst-tp="/ne:ne/shelf[shelf-id='1']/y"]/service-label""",
            DeleteEntry(
                """/ne:ne/services/CRS[src-tp="/ne:ne/shelf[shelf-id='1']/x"][dst-tp="/ne:ne/shelf[shelf-id='1']/y"]"""
            ),
        ),
    ],
)
def test_g30_release_rule(path: str, expected: Any) -> None:
    assert g30_config.release_rule(path) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (f"{G42_PORT}/admin-state", Reset("lock")),
        (f"{G42_PORT}/label", Reset("")),
        (f"{G42_PORT}/alarm-report-control", None),
        (f"{G42_PORT}/tom/phy-mode", None),
        (f"{G42_PORT}/tom/admin-state", Reset("lock")),
        ("/ioa-network-element:ne/facilities/super-channel-group[name='1-4-L1']/label", Reset("")),
        ("/ioa-network-element:ne/facilities/optical-carrier[name='1-4-L1-1']/frequency", None),
        (
            "/ioa-network-element:ne/facilities/super-channel[name='1-4-L1']/carrier-mode",
            DeleteEntry("/ioa-network-element:ne/facilities/super-channel[name='1-4-L1']"),
        ),
        (
            "/ioa-network-element:ne/services/xcon[name='7']/label",
            DeleteEntry("/ioa-network-element:ne/services/xcon[name='7']"),
        ),
    ],
)
def test_g42_release_rule(path: str, expected: Any) -> None:
    assert g42_config.release_rule(path) == expected


# ---------------------------------------------------------------------------
# Diff, apply, verify, release against a device
# ---------------------------------------------------------------------------


def test_apply_sends_only_the_difference_and_records_what_it_applied(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    device = _g30(
        monkeypatch,
        _g30_port_xml(**{"admin-status": "up", "service-label": "keep"}),
        _g30_port_xml(**{"admin-status": "down", "service-label": "keep"}),
    )
    node = _node(Platform.GROOVE_G30)
    port = _port("port-1/2/1", node)

    result = g30_port.set_port_admin_state(port, "down")

    (edit,) = device.edits()
    assert "<running/>" in edit
    assert "<admin-status>down</admin-status>" in edit
    assert edit.count("<port-id>") == 1
    assert "service-label" not in edit
    assert "commit" not in device.names()
    assert result["changed"] == {f"{G30_PORT}/admin-status": {"running": "up", "desired": "down"}}
    assert applied_config_store.locked == [node.subscription_instance_id]
    assert applied_config_store.rows == {
        (node.subscription_instance_id, f"{G30_PORT}/admin-status", port.subscription_instance_id): (
            "admin-state",
            "down",
        )
    }


def test_apply_on_a_converged_device_sends_nothing_but_still_records(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    device = _g30(monkeypatch, _g30_port_xml(**{"admin-status": "down"}))
    node = _node(Platform.GROOVE_G30)

    result = g30_port.set_port_admin_state(_port("port-1/2/1", node), "down")

    assert device.edits() == []
    assert result["added"] == result["changed"] == {}
    assert reconcile.golden_config(node) == {f"{G30_PORT}/admin-status": "down"}


def test_apply_fails_when_the_device_does_not_converge(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    _g30(monkeypatch, _g30_port_xml(**{"admin-status": "up"}))

    with pytest.raises(ConfigApplyError, match="did not converge"):
        g30_port.set_port_admin_state(_port("port-1/2/1", _node(Platform.GROOVE_G30)), "down")

    assert applied_config_store.rows == {}


def test_apply_is_refused_when_another_owner_applied_a_different_value(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    device = _g30(monkeypatch, _g30_port_xml(**{"admin-status": "up"}))
    node = _node(Platform.GROOVE_G30)
    applied_config_store.replace_applied_config(
        node.subscription_instance_id, uuid4(), "termination", {f"{G30_PORT}/admin-status": "up"}
    )

    with pytest.raises(ConfigConflictError, match="another product block"):
        g30_port.set_port_admin_state(_port("port-1/2/1", node), "down")

    assert device.edits() == []


def test_a_decimal_padded_differently_by_the_device_is_not_a_difference(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    xml = _g30_port_xml(
        **{
            "och-os": "<modulation-format>DP-QPSK</modulation-format><rate-class>100G</rate-class>"
            "<required-tx-optical-power>1.5</required-tx-optical-power>"
        }
    )
    device = _g30(monkeypatch, xml)
    node = _node(Platform.GROOVE_G30)
    och_os = g30_config.get_g30_client(node).data.ne_ne.shelf(1).slot(2).card.port(1).och_os

    diff = reconcile.diff_config(
        node, uuid4(), "tx-power:x", [fragment(och_os, required_tx_optical_power=Decimal("1.50"))]
    )

    assert not diff
    assert device.edits() == []


def test_g30_check_fiber_passes_when_the_port_runs_its_termination(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    node = _node(Platform.GROOVE_G30)
    remote = _port("1-A-1-L1", _node(Platform.FLEXILS, "flex.example.net"))
    _g30(
        monkeypatch,
        _g30_port_xml(
            **{"admin-status": "up", "external-connectivity": "yes", "connected-to": "flex.example.net 1-A-1-L1"}
        ),
    )

    g30_port.check_fiber(_port("port-1/2/1", node), remote, label="")


def test_g30_termination_of_an_ols_port_carries_the_pipe_label(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    """An Open Line System port carries the pipe label; a transponder port leaves it to its service."""
    node = _node(Platform.GROOVE_G30)
    _g30(monkeypatch, _g30_port_xml(**{"admin-status": "up"}))
    remote = _port("1-A-1-L1", _node(Platform.FLEXILS, "flex.example.net"))
    ols = _port("port-1/2/1", node, OpticalPortRole.OLS_LINE)
    transponder = _port("port-1/2/1", node, OpticalPortRole.TRANSPONDER_LINE)
    label = "OF-1 > flex.example.net 1-A-1-L1"

    (ols_fragment,) = g30_port.render_termination(ols, remote, label=label)
    (transponder_fragment,) = g30_port.render_termination(transponder, remote, label=label)

    assert ols_fragment.leaves[f"{G30_PORT}/service-label"] == "OF-1 > flex.example.net 1-A-1-L1"
    assert f"{G30_PORT}/service-label" not in transponder_fragment.leaves


def test_g30_check_fiber_reports_the_drift(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    node = _node(Platform.GROOVE_G30)
    remote = _port("1-A-1-L1", _node(Platform.FLEXILS, "flex.example.net"))
    device = _g30(monkeypatch, _g30_port_xml(**{"admin-status": "down", "external-connectivity": "yes"}))

    with pytest.raises(ConfigDriftError) as excinfo:
        g30_port.check_fiber(_port("port-1/2/1", node), remote, label="")

    assert "connected-to" in str(excinfo.value)
    assert "'running': 'down', 'desired': 'up'" in str(excinfo.value)
    assert device.edits() == []


def test_g30_factory_reset_writes_the_factory_values_and_drops_the_record(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    node = _node(Platform.GROOVE_G30)
    port = _port("port-1/2/1", node)
    remote = _port("1-A-1-L1", _node(Platform.FLEXILS, "flex.example.net"))
    configured = _g30_port_xml(
        **{"admin-status": "up", "external-connectivity": "yes", "connected-to": "flex.example.net 1-A-1-L1"}
    )
    device = _g30(monkeypatch, configured)
    g30_port.configure_termination(port, remote, label="")
    assert len(applied_config_store.rows) == 3

    result = g30_port.factory_reset(port, remote)

    (edit,) = device.edits()
    assert "<admin-status>down</admin-status>" in edit
    assert "<external-connectivity>no</external-connectivity>" in edit
    assert "<connected-to></connected-to>" in edit or "<connected-to/>" in edit
    assert set(result["reset"]) == {
        f"{G30_PORT}/admin-status",
        f"{G30_PORT}/external-connectivity",
        f"{G30_PORT}/connected-to",
    }
    assert applied_config_store.rows == {}


def test_release_leaves_what_another_owner_still_holds(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    node = _node(Platform.GROOVE_G30)
    port = _port("port-1/2/1", node)
    remote = _port("1-A-1-L1", _node(Platform.FLEXILS, "flex.example.net"))
    device = _g30(monkeypatch, _g30_port_xml(**{"admin-status": "up"}))
    service = uuid4()
    applied_config_store.replace_applied_config(
        node.subscription_instance_id, service, "client:port-1/2/1", {f"{G30_PORT}/admin-status": "up"}
    )

    result = g30_port.factory_reset(port, remote)

    assert f"{G30_PORT}/admin-status" not in result["reset"]
    assert "admin-status" not in device.edits()[0]
    assert list(applied_config_store.rows) == [(node.subscription_instance_id, f"{G30_PORT}/admin-status", service)]


def test_g30_align_tx_power_clamps_and_records_the_power(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    def och_os(power: str) -> str:
        return _g30_port_xml(
            **{
                "och-os": "<modulation-format>DP-QPSK</modulation-format><rate-class>100G</rate-class>"
                f"<required-tx-optical-power>{power}</required-tx-optical-power>"
            }
        )

    device = _g30(monkeypatch, och_os("-9.0"), och_os("-10.0"))
    node = _node(Platform.GROOVE_G30)
    owner = uuid4()

    g30_transponder.align_tx_power_to_target(node, "port-1/2/1", Decimal("5.0"), owner_instance_id=owner)

    assert "<required-tx-optical-power>-10.0</required-tx-optical-power>" in device.edits()[0]
    assert applied_config_store.applied_config(node.subscription_instance_id, owner, "tx-power:port-1/2/1") == {
        f"{G30_PORT}/och-os/required-tx-optical-power": "-10.0"
    }


def test_g42_apply_edits_the_candidate_and_commits(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    device = _g42(monkeypatch, _g42_port_xml(**{"admin-state": "unlock"}), _g42_port_xml(**{"admin-state": "lock"}))

    g42_port.set_port_admin_state(_port("1-4-L1", _node(Platform.GX_G42)), "down")

    names = device.names()
    (edit,) = device.edits()
    assert names.index("edit-config") < names.index("commit")
    assert "<candidate/>" in edit
    assert "<admin-state>lock</admin-state>" in edit


def test_g42_rpc_error_surfaces_with_its_error_tag(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    _g42(
        monkeypatch,
        _g42_port_xml(**{"admin-state": "lock"}),
        dispatch_error=rpc_error("operation-failed", "boom"),
    )

    with pytest.raises(RuntimeError, match="boom") as excinfo:
        g42_port.set_port_admin_state(_port("1-4-L1", _node(Platform.GX_G42)), "up")

    assert getattr(excinfo.value, "rpc_error_tag", None) == "operation-failed"
    assert applied_config_store.rows == {}


def test_g42_line_release_deletes_the_super_channel_and_resets_the_ports(
    monkeypatch: pytest.MonkeyPatch, applied_config_store: AppliedConfigStore
) -> None:
    device = _g42(monkeypatch, _g42_port_xml(**{"admin-state": "unlock"}))
    node = _node(Platform.GX_G42)

    result = g42_transponder.factory_reset_transponder_lines(node, ["1-4-L1"], owner_instance_id=uuid4())

    removal, resets = device.edits()
    assert 'operation="remove"' in removal
    assert "<super-channel" in removal
    assert "<name>1-4-L1</name>" in removal
    assert "<admin-state>lock</admin-state>" in resets
    assert result["deleted"] == ["/ioa-network-element:ne/facilities/super-channel[name='1-4-L1']"]


def test_unsupported_platform_has_no_declarative_configuration(applied_config_store: AppliedConfigStore) -> None:
    with pytest.raises(NotImplementedError):
        reconcile.diff_config(_node(Platform.FLEXILS), UUID(int=1), "x", [])


# ---------------------------------------------------------------------------
# Node role (read-only)
# ---------------------------------------------------------------------------


def test_g30_role_requests_the_card_types_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """The role is read with one subtree filter selecting the card types, not the shelf tree."""

    def subslot(subslot_id: int, card_type: str) -> str:
        return (
            f"<subslot><subslot-id>{subslot_id}</subslot-id>"
            f"<subcard><required-type>{card_type}</required-type></subcard></subslot>"
        )

    def slot(slot_id: int, card_type: str, subslots: str = "") -> str:
        card = f"<card><required-type>{card_type}</required-type>{subslots}</card>"
        return f"<slot><slot-id>{slot_id}</slot-id>{card}</slot>"

    device = _g30(
        monkeypatch,
        '<ne xmlns="http://coriant.com/yang/os/ne"><shelf><shelf-id>1</shelf-id><slot><slot-id>1</slot-id></slot>'
        + slot(2, "CHM2T")
        + slot(3, "OCC2", subslot(1, "CAD8EOFP2") + subslot(2, "BAXOFP2") + subslot(3, "NOT-A-CARD"))
        + slot(5, "PSU")
        + "</shelf></ne>",
    )

    assert g30_node.role(_node(Platform.GROOVE_G30)) is OpticalNodeRole.TRANSPONDER_FOADM

    ((rpc, (_source, (filter_type, selection))),) = device.calls
    assert (rpc, filter_type) == ("get-config", "subtree")
    selected = etree.fromstring(selection) if isinstance(selection, str) else selection
    leaves = sorted(
        "/".join(etree.QName(node).localname for node in [*reversed(list(leaf.iterancestors())), leaf])
        for leaf in selected.iter()
        if len(leaf) == 0
    )
    assert leaves == [
        "ne/shelf/shelf-id",
        "ne/shelf/slot/card/required-type",
        "ne/shelf/slot/card/subslot/subcard/required-type",
        "ne/shelf/slot/card/subslot/subslot-id",
        "ne/shelf/slot/slot-id",
    ]
