"""Unit tests for the vendor-agnostic HAL helpers in ``hal/_common.py``.

These helpers are pure (or take an injected callback), so they are exercised
directly with lightweight fakes for the block objects whose attributes they read.
"""

from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest

from orchestrator.optical.hal._common import (
    ROLE_ORDER,
    UnsupportedPortRoleError,
    _as_decimal,
    _as_flexils_block,
    _as_g30_block,
    _as_g42_block,
    _extract_remote_port_id,
    _node_id,
    _port_name,
    _ports_by_role,
    _same_node,
    _vendor_platform,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30BlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole

_PORT_NAMES: dict[OpticalPortRole, list[str]] = {
    OpticalPortRole.OLS_LINE: ["port-line", "port-shared"],
    OpticalPortRole.OLS_ADD_DROP: ["port-shared", "port-add-drop"],
    OpticalPortRole.TRANSPONDER_LINE: ["port-line-2"],
}


def _management(
    vendor: Vendor | str = Vendor.NOKIA,
    platform: Platform | str = Platform.FLEXILS,
    fqdn: str | None = "node.example.com",
) -> SimpleNamespace:
    return SimpleNamespace(
        optical_module_node_vendor=vendor,
        optical_module_node_platform=platform,
        optical_module_node_fqdn=fqdn,
    )


def _node_block(block_cls: type, vendor: Vendor, platform: Platform, fqdn: str | None = "node.example.com") -> Any:
    subscription_id = uuid4()
    return block_cls.model_construct(
        name=block_cls.__name__,
        subscription_instance_id=subscription_id,
        owner_subscription_id=subscription_id,
        management=_management(vendor, platform, fqdn),
    )


def _names_for_role(role: OpticalPortRole) -> list[str]:
    return list(_PORT_NAMES[role])


def test_ports_by_role_default_selects_supported_roles_in_role_order() -> None:
    supported = frozenset({OpticalPortRole.TRANSPONDER_LINE, OpticalPortRole.OLS_LINE, OpticalPortRole.OLS_ADD_DROP})

    result = _ports_by_role(supported, _names_for_role, None)

    assert result == ["port-line", "port-shared", "port-add-drop", "port-line-2"]


def test_ports_by_role_explicit_roles_preserve_requested_order() -> None:
    supported = frozenset(ROLE_ORDER)

    result = _ports_by_role(
        supported,
        _names_for_role,
        [OpticalPortRole.TRANSPONDER_LINE, OpticalPortRole.OLS_LINE],
    )

    assert result == ["port-line-2", "port-line", "port-shared"]


def test_ports_by_role_deduplicates_preserving_first_seen_order() -> None:
    supported = frozenset({OpticalPortRole.OLS_LINE, OpticalPortRole.OLS_ADD_DROP})

    result = _ports_by_role(supported, _names_for_role, None)

    assert result == ["port-line", "port-shared", "port-add-drop"]


def test_ports_by_role_rejects_explicit_unsupported_role() -> None:
    supported = frozenset({OpticalPortRole.OLS_LINE})

    with pytest.raises(UnsupportedPortRoleError, match="not supported"):
        _ports_by_role(supported, _names_for_role, [OpticalPortRole.TRANSPONDER_LINE])


def test_vendor_platform_reads_management_key() -> None:
    block = SimpleNamespace(management=_management(Vendor.NOKIA, Platform.GROOVE_G30))

    assert _vendor_platform(block) == (Vendor.NOKIA, Platform.GROOVE_G30)


def test_node_id_returns_fqdn() -> None:
    block = SimpleNamespace(management=_management(fqdn="node-01.example.com"))

    assert _node_id(block) == "node-01.example.com"


def test_node_id_falls_back_when_fqdn_missing() -> None:
    block = SimpleNamespace(management=_management(fqdn=None))

    assert _node_id(block) == "<no fqdn>"


def test_same_node_identity() -> None:
    block = SimpleNamespace(management=_management())

    assert _same_node(block, block) is True


def test_same_node_equal_fqdn() -> None:
    first = SimpleNamespace(management=_management(fqdn="a.example.com"))
    second = SimpleNamespace(management=_management(fqdn="a.example.com"))

    assert _same_node(first, second) is True


def test_same_node_different_fqdn() -> None:
    first = SimpleNamespace(management=_management(fqdn="a.example.com"))
    second = SimpleNamespace(management=_management(fqdn="b.example.com"))

    assert _same_node(first, second) is False


def test_same_node_missing_fqdn_is_not_equal() -> None:
    first = SimpleNamespace(management=_management(fqdn=None))
    second = SimpleNamespace(management=_management(fqdn=None))

    assert _same_node(first, second) is False


def test_as_flexils_block_returns_matching_block() -> None:
    block = _node_block(NokiaFlexIlsBlockProvisioning, Vendor.NOKIA, Platform.FLEXILS)

    assert _as_flexils_block(block) is block


def test_as_flexils_block_rejects_other_vendor() -> None:
    other = _node_block(NokiaGrooveG30BlockProvisioning, Vendor.NOKIA, Platform.GROOVE_G30)

    with pytest.raises(TypeError, match="Expected a NokiaFlexIlsBlock"):
        _as_flexils_block(other)


def test_as_g30_block_returns_matching_block() -> None:
    block = _node_block(NokiaGrooveG30BlockProvisioning, Vendor.NOKIA, Platform.GROOVE_G30)

    assert _as_g30_block(block) is block


def test_as_g30_block_rejects_other_vendor() -> None:
    other = _node_block(NokiaGxG42BlockProvisioning, Vendor.NOKIA, Platform.GX_G42)

    with pytest.raises(TypeError, match="Expected a NokiaGrooveG30Block"):
        _as_g30_block(other)


def test_as_g42_block_returns_matching_block() -> None:
    block = _node_block(NokiaGxG42BlockProvisioning, Vendor.NOKIA, Platform.GX_G42)

    assert _as_g42_block(block) is block


def test_as_g42_block_rejects_other_vendor() -> None:
    other = _node_block(NokiaFlexIlsBlockProvisioning, Vendor.NOKIA, Platform.FLEXILS)

    with pytest.raises(TypeError, match="Expected a NokiaGxG42Block"):
        _as_g42_block(other)


def test_port_name_returns_name() -> None:
    assert _port_name(SimpleNamespace(optical_port_name="port-1/2/3")) == "port-1/2/3"


def test_port_name_raises_when_missing() -> None:
    with pytest.raises(ValueError, match="has no port name"):
        _port_name(SimpleNamespace(optical_port_name=None))


@pytest.mark.parametrize(
    ("port_name", "expected"),
    [
        ("port-1/2/3", "1-2-3"),
        ("G-1.4", "1-4"),
        ("abc-9.0_y", "9-0-y"),
        ("a1b2", "1b2"),
        ("port-1", "1"),
    ],
)
def test_extract_remote_port_id(port_name: str, expected: str) -> None:
    assert _extract_remote_port_id(port_name) == expected


def test_extract_remote_port_id_raises_without_digit() -> None:
    with pytest.raises(ValueError, match="Could not extract port identifier"):
        _extract_remote_port_id("no-digits-here")


def test_as_decimal_accepts_decimal_unchanged() -> None:
    value = Decimal("1.25")

    assert _as_decimal(value) is value


def test_as_decimal_accepts_float_and_string() -> None:
    assert _as_decimal(1.5) == Decimal("1.5")
    assert _as_decimal("2.75") == Decimal("2.75")


def test_as_decimal_rejects_other_types() -> None:
    with pytest.raises(TypeError, match="must be of type Decimal"):
        _as_decimal(cast(Any, 1))
