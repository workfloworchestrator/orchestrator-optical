"""Unit tests for the fiber span node-role gate.

``SPAN_NODE_ROLES`` is the single source of truth for which node roles can
terminate a fiber span: it drives both the interactive
``create_pipe_form_pages`` selector and the bulk task ``_check_span_nodes``
guard. Amplifiers (FlexILS OLA/OA) must be accepted — both ROADM↔amplifier
and amplifier↔amplifier — while plain-transponder nodes stay rejected.
"""

from types import SimpleNamespace

import pytest

from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.workflows.optical_pipe.shared import SPAN_NODE_ROLES
from orchestrator.optical.workflows.tasks import bulk_create_optical_pipes as bulk_pipes
from orchestrator.optical.workflows.tasks.bulk_create_optical_pipes import _check_span_nodes


def _node_block(role: OpticalNodeRole, fqdn: str = "node.optical.test") -> SimpleNamespace:
    return SimpleNamespace(
        optical_node_role=role,
        management=SimpleNamespace(
            optical_module_node_fqdn=fqdn,
            optical_module_node_vendor=Vendor.NOKIA,
            optical_module_node_platform=Platform.FLEXILS,
        ),
    )


def test_span_node_roles_accepts_amplifiers() -> None:
    """Spans terminate on ROADM, xOADM and amplifier line-system nodes — never on plain transponders."""
    assert OpticalNodeRole.ROADM in SPAN_NODE_ROLES
    assert OpticalNodeRole.TRANSPONDER_XOADM in SPAN_NODE_ROLES
    assert OpticalNodeRole.AMPLIFIER in SPAN_NODE_ROLES
    assert OpticalNodeRole.TRANSPONDER not in SPAN_NODE_ROLES


def _check(monkeypatch: pytest.MonkeyPatch, role_a: OpticalNodeRole, role_b: OpticalNodeRole) -> None:
    blocks = {"node-a": _node_block(role_a, "a.optical.test"), "node-b": _node_block(role_b, "b.optical.test")}
    monkeypatch.setattr(bulk_pipes, "node_block_from_instance", blocks.__getitem__)
    _check_span_nodes("node-a", "node-b", 3)


def test_check_span_nodes_accepts_roadm_amplifier(monkeypatch: pytest.MonkeyPatch) -> None:
    """The reported failure: ROADM --- ILA must pass the bulk span guard."""
    _check(monkeypatch, OpticalNodeRole.ROADM, OpticalNodeRole.AMPLIFIER)


def test_check_span_nodes_accepts_amplifier_amplifier(monkeypatch: pytest.MonkeyPatch) -> None:
    """ILA --- ILA spans are allowed as transit segments."""
    _check(monkeypatch, OpticalNodeRole.AMPLIFIER, OpticalNodeRole.AMPLIFIER)


def test_check_span_nodes_rejects_transponder(monkeypatch: pytest.MonkeyPatch) -> None:
    """Plain-transponder ends (e.g. GX G42) still cannot terminate a span."""
    with pytest.raises(ValueError, match="cannot terminate a fiber span"):
        _check(monkeypatch, OpticalNodeRole.ROADM, OpticalNodeRole.TRANSPONDER)


def test_check_span_nodes_rejects_vendor_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Same-vendor rule still applies to amplifier spans."""
    blocks = {
        "node-a": _node_block(OpticalNodeRole.ROADM, "a.optical.test"),
        "node-b": SimpleNamespace(
            optical_node_role=OpticalNodeRole.AMPLIFIER,
            management=SimpleNamespace(
                optical_module_node_fqdn="b.optical.test",
                optical_module_node_vendor=Vendor.NOKIA,
                optical_module_node_platform=Platform.GROOVE_G30,
            ),
        ),
    }
    monkeypatch.setattr(bulk_pipes, "node_block_from_instance", blocks.__getitem__)
    with pytest.raises(ValueError, match="same vendor and platform"):
        _check_span_nodes("node-a", "node-b", 3)
