"""Vendor-agnostic shared helpers for the optical HAL.

This module holds the cross-device, cross-area building blocks used by the
per-device adapters under :mod:`orchestrator.optical.hal.adapters`: the
vendor/platform dispatch key, the narrowing helpers to the concrete vendor
blocks, the shared error type and the small node/port accessor helpers. It must
not import from any adapter, so that the dependency direction stays
``_common`` <- ``adapters.<device>.*`` <- ``hal.<area>``.
"""

from __future__ import annotations

import importlib
import re
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from orchestrator.optical.hal.sessions import shared_session
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
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
#: :func:`_ports_grouped_by_role` deterministic regardless of the node's vendor.
ROLE_ORDER: tuple[OpticalPortRole, ...] = (
    OpticalPortRole.OLS_LINE,
    OpticalPortRole.OLS_ADD_DROP,
    OpticalPortRole.TRANSPONDER_CLIENT,
    OpticalPortRole.TRANSPONDER_LINE,
    OpticalPortRole.COHERENT_PLUGGABLE,
)


@dataclass(frozen=True)
class IntraNodeEdge:
    """An internal route of an Optical Node from an add/drop port to an OLS line port.

    Attributes:
        add_drop_port: Device name of the add/drop port the route starts from.
        line_port: Device name of the OLS line port (the degree) the route reaches.
        used_passbands: The ``[start, end)`` passbands (MHz) already occupied on the
            internal route by the circuits provisioned on the device, merged and sorted.
            The occupation of the line port itself is *not* included: it is stored on
            the line port block and accounted for by the path engine.
    """

    add_drop_port: str
    line_port: str
    used_passbands: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class OpticalNodeDiscovery:
    """What an Optical Node reports about itself, read before the node is modelled.

    Attributes:
        name: The name configured on the device (``ne-name`` on the NETCONF devices, the
            Target Identifier on FlexILS); ``None`` when the device has none.
        role: The node role derived from the installed hardware.
        software_version: The active software version.
        flexils_gmpls_id: The GMPLS router id of a FlexILS node; ``None`` on the other platforms.
    """

    name: str | None
    role: OpticalNodeRole
    software_version: str
    flexils_gmpls_id: str | None = None


class UnsupportedPlatformError(NotImplementedError):
    """Raised when a HAL operation has no implementation for the node's vendor/platform."""


class UnsupportedPortRoleError(NotImplementedError):
    """Raised when a port role is requested that the node's vendor/platform cannot enumerate."""


class VendorSdkNotInstalledError(ImportError):
    """Raised when a device adapter is used but the vendor SDK it drives is not installed.

    The vendor SDKs are not distributed with this package: install the SDK package named
    in the message into the same environment (see the README, "Vendor SDKs").
    """

    def __init__(self, sdk: str, device: str) -> None:
        """Build the error for the missing ``sdk`` package of ``device``."""
        super().__init__(f"The {device} adapter requires the {sdk!r} SDK package, which is not installed", name=sdk)


def _retrieve_required[T](retrieve: Callable[..., T | None], **kwargs: Any) -> T:
    """Read an object from the device, raising when it does not exist.

    A NETCONF read of an object that does not exist returns no data (``None``) instead of
    failing; HAL operations need the object, so they fail loudly here.

    Args:
        retrieve: The bound ``retrieve`` method of an SDK navigator node.
        **kwargs: The ``retrieve`` arguments (``depth``, ``content``, ...).

    Returns:
        The object read from the device.

    Raises:
        ValueError: If the device returned no data for the object.
    """
    value = retrieve(**kwargs)
    if value is None:
        node = getattr(retrieve, "__self__", None)
        where = node.instance_identifier() if hasattr(node, "instance_identifier") else repr(node)
        msg = f"The device returned no data for {where}"
        raise ValueError(msg)
    return value


def _connect_first[ClientT](
    client_cls: Callable[..., ClientT],
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    **client_kwargs: Any,
) -> ClientT:
    """Return a device session on the first reachable management IP of a node.

    The DCN loopback IP is tried first, then the DCN interface IP (see :func:`_connect_hosts`).

    Args:
        client_cls: The SDK client class (its constructor opens the session).
        optical_node_block: The Optical Node block whose management IPs are tried.
        **client_kwargs: Credentials and options passed to every connection attempt.

    Returns:
        The connected client.

    Raises:
        ValueError: If the node has no management IP.
        ExceptionGroup: If no management IP is reachable (one exception per attempt).
    """
    management = optical_node_block.management
    hosts = _management_hosts(
        management.optical_module_node_management_loopback_ip, management.optical_module_node_management_ip
    )
    return _connect_hosts(client_cls, hosts, management.optical_module_node_name, **client_kwargs)


def _management_hosts(*management_ips: object) -> tuple[str, ...]:
    """Return the given management IPs as connection hosts, in order, without the unset ones."""
    return tuple(str(ip) for ip in management_ips if ip is not None)


def _connect_hosts[ClientT](
    client_cls: Callable[..., ClientT],
    hosts: tuple[str, ...],
    name: str | None = None,
    **client_kwargs: Any,
) -> ClientT:
    """Return a device session on the first of ``hosts`` that accepts it.

    The NETCONF clients take a single host and open the session in their constructor.
    Within a :func:`~orchestrator.optical.hal.sessions.device_sessions` scope the session
    to the node is reused (one left open by an earlier scope, when there is one). This is
    the entry point for a node that has no block yet (discovery from a create form); a
    modelled node goes through :func:`_connect_first`.

    Args:
        client_cls: The SDK client class (its constructor opens the session).
        hosts: The management IPs to try, in order.
        name: The node name, used in the error messages only (the hosts when not known).
        **client_kwargs: Credentials and options passed to every connection attempt.

    Returns:
        The connected client.

    Raises:
        ValueError: If there is no host to connect to.
        ExceptionGroup: If no host is reachable (one exception per attempt).
    """
    if not hosts:
        msg = f"Node {name} has no management IP to connect to" if name else "No management IP to connect to"
        raise ValueError(msg)
    return shared_session(
        (client_cls, hosts),
        lambda: _open_first(client_cls, hosts, name or "/".join(hosts), client_kwargs),
        _netconf_session_alive,
    )


def _netconf_session_alive(client: Any) -> bool:
    """Tell whether an idle NETCONF session is still open (the device may have dropped it meanwhile).

    The SDK clients expose no liveness check: this reads the ncclient manager they hold.
    """
    manager = getattr(client, "_manager", None)
    return manager is not None and bool(getattr(manager, "connected", True))


def _open_first[ClientT](
    client_cls: Callable[..., ClientT], hosts: tuple[str, ...], name: str, client_kwargs: dict[str, Any]
) -> ClientT:
    """Open a new session on the first of ``hosts`` that accepts it (see :func:`_connect_first`)."""
    errors: list[Exception] = []
    for host in hosts:
        try:
            return client_cls(management_ip=host, **client_kwargs)
        except Exception as exc:  # noqa: BLE001 - each attempt's failure is reported in the group
            errors.append(exc)
    # The causes go in the message: WFO stores a failed step's message and traceback,
    # neither of which shows the sub-exceptions of a group.
    causes = "; ".join(f"{host}: {type(exc).__name__}: {exc}" for host, exc in zip(hosts, errors, strict=True))
    msg = f"Could not connect to node {name} ({causes})"
    raise ExceptionGroup(msg, errors)


class LazyAdapter:
    """A device adapter module imported on first attribute access.

    The adapters import their vendor SDK at module level; the area dispatchers hold
    them through this proxy so that importing :mod:`orchestrator.optical.hal` (and the
    workflows) works without any vendor SDK installed. A missing SDK only surfaces,
    as :class:`VendorSdkNotInstalledError`, when a node of that platform is driven.
    """

    def __init__(self, module_name: str) -> None:
        """Proxy the adapter module ``module_name`` (fully qualified)."""
        self._module_name = module_name

    def __getattr__(self, name: str) -> Any:
        """Import the adapter module (cached by :mod:`sys.modules`) and return its attribute."""
        return getattr(importlib.import_module(self._module_name), name)


def _ports_grouped_by_role(
    supported_roles: frozenset[OpticalPortRole],
    port_names_for_role: Callable[[OpticalPortRole], list[str]],
    roles: list[OpticalPortRole] | None,
) -> dict[OpticalPortRole, list[str]]:
    """Return the device port names of a node for the requested roles, keyed by role.

    Args:
        supported_roles: The roles the node's vendor/platform can enumerate.
        port_names_for_role: Resolves a single role to its device port names (may hit the device).
        roles: The roles to collect; ``None`` selects every supported role.

    Returns:
        The port names of each requested role; the roles are in the requested order
        (:data:`ROLE_ORDER` when ``roles`` is ``None``).

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

    return {role: list(port_names_for_role(role)) for role in requested}


def _all_ports(ports_by_role: dict[OpticalPortRole, list[str]]) -> list[str]:
    """Return the de-duplicated port names of a role-keyed enumeration, in its order."""
    return list(dict.fromkeys(name for names in ports_by_role.values() for name in names))


def _vendor_platform(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> tuple[Vendor, Platform]:
    """Return the ``(vendor, platform)`` dispatch key of the given Optical Node block."""
    return (
        optical_node_block.management.optical_module_node_vendor,
        optical_node_block.management.optical_module_node_platform,
    )


def _node_id(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> str:
    """Return the device-side node name of the given Optical Node block.

    A Nokia FlexILS node is identified on the device by its GMPLS NENAME, i.e. its
    Target Identifier (TID), which may differ from its name (e.g. ``flex.ba01`` vs
    ``flex.ba01.exa.it``). Every other platform uses the node name of the management block. This is
    the name to use in device identifiers (OEL ``SRCNODENAME``/``DSTNODENAME``,
    OSNC ``REMNODETID``, SCG ``PROVOWREMPTP``, ...) and in messages.
    """
    if isinstance(optical_node_block, NokiaFlexIlsBlockProvisioning) and (
        target_id := getattr(optical_node_block, "optical_flexils_target_id", None)
    ):
        return target_id
    name = optical_node_block.management.optical_module_node_name
    return name if name is not None else "<no name>"


def _same_node(
    node_a: AnyOpticalNodeBlockProvisioningUnion,
    node_b: AnyOpticalNodeBlockProvisioningUnion,
) -> bool:
    """Return whether two Optical Node blocks refer to the same device."""
    if node_a is node_b:
        return True
    name_a = node_a.management.optical_module_node_name
    name_b = node_b.management.optical_module_node_name
    return name_a is not None and name_a == name_b


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
