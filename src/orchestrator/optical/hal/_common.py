"""Vendor-agnostic shared helpers for the optical HAL.

This module holds the cross-device, cross-area building blocks used by the
per-device adapters under :mod:`orchestrator.optical.hal.adapters`: the
vendor/platform dispatch key, the narrowing helpers to the concrete vendor
blocks, the shared error type and the small node/port accessor helpers. It must
not import from any adapter, so that the dependency direction stays
``_common`` <- ``adapters.<device>.*`` <- ``hal.<area>``.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from decimal import Decimal

from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30BlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole
from orchestrator.optical.products.product_blocks.optical_port.unions import AnyOpticalPortBlockProvisioning

#: Canonical order of port roles, used to make the "all roles" default of
#: :func:`_ports_by_role` deterministic regardless of the node's vendor.
ROLE_ORDER: tuple[OpticalPortRole, ...] = (
    OpticalPortRole.OLS_LINE,
    OpticalPortRole.OLS_ADD_DROP,
    OpticalPortRole.TRANSPONDER_CLIENT,
    OpticalPortRole.TRANSPONDER_LINE,
    OpticalPortRole.COHERENT_PLUGGABLE,
)


class UnsupportedPlatformError(NotImplementedError):
    """Raised when a HAL operation has no implementation for the node's vendor/platform."""


class UnsupportedPortRoleError(NotImplementedError):
    """Raised when a port role is requested that the node's vendor/platform cannot enumerate."""


def _ports_by_role(
    supported_roles: frozenset[OpticalPortRole],
    port_names_for_role: Callable[[OpticalPortRole], list[str]],
    roles: list[OpticalPortRole] | None,
) -> list[str]:
    """Return the de-duplicated device port names of a node for the requested roles.

    Args:
        supported_roles: The roles the node's vendor/platform can enumerate.
        port_names_for_role: Resolves a single role to its device port names (may hit the device).
        roles: The roles to collect; ``None`` selects every supported role.

    Returns:
        The port names of the requested roles, de-duplicated, in :data:`ROLE_ORDER`.

    Raises:
        UnsupportedPortRoleError: If an explicitly requested role is not in ``supported_roles``.
    """
    if roles is None:
        requested = [role for role in ROLE_ORDER if role in supported_roles]
    else:
        requested = list(roles)
        for role in requested:
            if role not in supported_roles:
                msg = f"Port role {role.value} is not supported by this node"
                raise UnsupportedPortRoleError(msg)

    port_names: list[str] = []
    for role in requested:
        port_names.extend(port_names_for_role(role))
    return list(dict.fromkeys(port_names))


def _vendor_platform(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> tuple[Vendor, Platform]:
    """Return the ``(vendor, platform)`` dispatch key of the given Optical Node block."""
    return (
        optical_node_block.management.optical_module_node_vendor,
        optical_node_block.management.optical_module_node_platform,
    )


def _node_id(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> str:
    """Return the fqdn of the given Optical Node block, for use in identifiers and messages."""
    fqdn = optical_node_block.management.optical_module_node_fqdn
    return fqdn if fqdn is not None else "<no fqdn>"


def _same_node(
    node_a: AnyOpticalNodeBlockProvisioningUnion,
    node_b: AnyOpticalNodeBlockProvisioningUnion,
) -> bool:
    """Return whether two Optical Node blocks refer to the same device."""
    if node_a is node_b:
        return True
    fqdn_a = node_a.management.optical_module_node_fqdn
    fqdn_b = node_b.management.optical_module_node_fqdn
    return fqdn_a is not None and fqdn_a == fqdn_b


def _as_flexils_block(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> NokiaFlexIlsBlockProvisioning:
    """Narrow an Optical Node block to the Nokia FlexILS block type."""
    if not isinstance(optical_node_block, NokiaFlexIlsBlockProvisioning):
        msg = f"Expected a NokiaFlexIlsBlock, got {type(optical_node_block).__name__}"
        raise TypeError(msg)
    return optical_node_block


def _as_g30_block(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> NokiaGrooveG30BlockProvisioning:
    """Narrow an Optical Node block to the Nokia Groove G30 block type."""
    if not isinstance(optical_node_block, NokiaGrooveG30BlockProvisioning):
        msg = f"Expected a NokiaGrooveG30Block, got {type(optical_node_block).__name__}"
        raise TypeError(msg)
    return optical_node_block


def _as_g42_block(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> NokiaGxG42BlockProvisioning:
    """Narrow an Optical Node block to the Nokia GX G42 block type."""
    if not isinstance(optical_node_block, NokiaGxG42BlockProvisioning):
        msg = f"Expected a NokiaGxG42Block, got {type(optical_node_block).__name__}"
        raise TypeError(msg)
    return optical_node_block


def _port_name(port_block: AnyOpticalPortBlockProvisioning) -> str:
    """Return the device-side name of the given Optical Port block."""
    name = port_block.optical_port_name
    if name is None:
        msg = f"Optical port block {type(port_block).__name__} has no port name"
        raise ValueError(msg)
    return name


def _extract_remote_port_id(port_name: str) -> str:
    """Extract and format the port id from a port name.

    Args:
        port_name: The name of the remote port.

    Returns:
        The port id, starting from the first digit of the name, with every
        non-alphanumeric character replaced by a dash.

    Raises:
        ValueError: If no digit can be found in the port name.
    """
    match = re.search(r"\d", port_name)
    if match is None:
        msg = f"Could not extract port identifier from remote port name: {port_name}"
        raise ValueError(msg)
    port_id = port_name[match.start() :]
    return re.sub(r"[^a-zA-Z0-9]", "-", port_id)


def _as_decimal(value: Decimal | float | str) -> Decimal:
    """Normalize a power difference to a ``Decimal``."""
    if isinstance(value, float):
        value = str(value)
    if isinstance(value, str):
        value = Decimal(value)
    if not isinstance(value, Decimal):
        msg = "value must be of type Decimal at this point."
        raise TypeError(msg)
    return value
