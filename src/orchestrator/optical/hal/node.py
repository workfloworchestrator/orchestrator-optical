"""Node-area HAL: client/discovery access and the node-level retrieve dispatchers.

The client factories and the FlexILS SNE discovery logic live in the per-device
adapters (see :mod:`orchestrator.optical.hal.adapters`); this module re-exports
the client factories and provides the vendor-dispatching retrieve
operations, routing with ``match/case`` on the node's vendor and platform.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from orchestrator.optical.hal._common import (
    LazyAdapter,
    OpticalNodeDiscovery,
    UnsupportedPlatformError,
    _as_flexils_block,
    _as_g30_block,
    _as_g42_block,
    _management_hosts,
    _vendor_platform,
)
from orchestrator.optical.hal.adapters.nokia_flexils.gne import FlexilsGneProvider
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor

if TYPE_CHECKING:
    from orchestrator.optical.hal.adapters.nokia_flexils import _shared as flexils_shared
    from orchestrator.optical.hal.adapters.nokia_flexils import node as flexils
    from orchestrator.optical.hal.adapters.nokia_flexils._shared import FlexilsClient
    from orchestrator.optical.hal.adapters.nokia_groove_g30 import _shared as groove_g30_shared
    from orchestrator.optical.hal.adapters.nokia_groove_g30 import node as groove_g30
    from orchestrator.optical.hal.adapters.nokia_groove_g30._sdk import G30Client
    from orchestrator.optical.hal.adapters.nokia_gx_g42 import _shared as gx_g42_shared
    from orchestrator.optical.hal.adapters.nokia_gx_g42 import node as gx_g42
    from orchestrator.optical.hal.adapters.nokia_gx_g42._sdk import G42Client
    from orchestrator.optical.products.product_blocks.optical_location import OpticalModuleLocationBlockProvisioning
    from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning
    from orchestrator.optical.utils.custom_types.ip_address import IPAddress
else:
    flexils_shared = LazyAdapter("orchestrator.optical.hal.adapters.nokia_flexils._shared")
    flexils = LazyAdapter("orchestrator.optical.hal.adapters.nokia_flexils.node")
    groove_g30_shared = LazyAdapter("orchestrator.optical.hal.adapters.nokia_groove_g30._shared")
    gx_g42_shared = LazyAdapter("orchestrator.optical.hal.adapters.nokia_gx_g42._shared")
    groove_g30 = LazyAdapter("orchestrator.optical.hal.adapters.nokia_groove_g30.node")
    gx_g42 = LazyAdapter("orchestrator.optical.hal.adapters.nokia_gx_g42.node")

__all__ = [
    "FlexilsGneProvider",
    "OpticalNodeDiscovery",
    "discover_flexils_node",
    "discover_optical_node",
    "get_flex_client",
    "get_g30_client",
    "get_g42_client",
    "get_optical_node_client",
    "retrieve_omses_terminating_on_device",
    "retrieve_optical_node_role_and_software_version",
    "retrieve_ports_spectral_occupations",
    "retrieve_software_version",
]


def get_flex_client(optical_node_block: NokiaFlexIlsBlockProvisioning) -> FlexilsClient:
    """Return a TL1 client to reach the given Nokia FlexILS node (see the FlexILS adapter)."""
    return flexils_shared.get_flex_client(optical_node_block)


def get_g30_client(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> G30Client:
    """Return a NETCONF client connected to the given Nokia Groove G30 node (see the G30 adapter)."""
    return groove_g30_shared.get_g30_client(optical_node_block)


def get_g42_client(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> G42Client:
    """Return a NETCONF client connected to the given Nokia GX G42 node (see the G42 adapter)."""
    return gx_g42_shared.get_g42_client(optical_node_block)


def discover_flexils_node(
    optical_flexils_target_id: str,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
    optical_flexils_gmpls_id: IPAddress | None = None,
    location: OpticalModuleLocationBlockProvisioning | None = None,
) -> tuple[OpticalNodeRole, str]:
    """Discover the role and software version of a Nokia FlexILS node (see the FlexILS adapter)."""
    return flexils_shared.discover_flexils_node(
        optical_flexils_target_id,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
        optical_flexils_gmpls_id=optical_flexils_gmpls_id,
        location=location,
    )


def discover_optical_node(
    vendor: Vendor,
    platform: Platform,
    *,
    dcn_loopback_ip: IPAddress | None = None,
    dcn_interface_ip: IPAddress | None = None,
    flexils_target_id: str | None = None,
    location: OpticalModuleLocationBlockProvisioning | None = None,
) -> OpticalNodeDiscovery:
    """Read what a node reports about itself, before it is modelled: name, role, software version.

    This is the discovery behind the create forms: the user gives how to reach the node
    and the rest is read from it. The NETCONF devices (Groove G30, GX G42) are reached
    at their DCN IPs (loopback first) and report their ``ne-name``. A FlexILS node is
    identified by its Target ID, which is also its name; it is reached at its DCN IPs
    or, without any, through the GNE closest to its location, and it reports its GMPLS ID.

    Args:
        vendor: Vendor of the node.
        platform: Platform of the node.
        dcn_loopback_ip: Loopback IP of the node's DCN interface.
        dcn_interface_ip: Interface IP of the node's DCN interface.
        flexils_target_id: Target ID of a FlexILS node (required for FlexILS).
        location: The Optical Location block hosting the node (FlexILS without a DCN IP).

    Returns:
        The discovered node properties.

    Raises:
        ValueError: If the node cannot be reached, identified or queried.
        ExceptionGroup: If no DCN IP of a NETCONF device is reachable.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match (vendor, platform):
        case (Vendor.NOKIA, Platform.FLEXILS):
            if not flexils_target_id:
                msg = "The Target ID is required to discover a FlexILS node"
                raise ValueError(msg)
            return flexils_shared.discover(
                flexils_target_id,
                optical_management_ip=dcn_interface_ip,
                optical_loopback_ip=dcn_loopback_ip,
                location=location,
            )
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.discover(_management_hosts(dcn_loopback_ip, dcn_interface_ip))
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.discover(_management_hosts(dcn_loopback_ip, dcn_interface_ip))
        case _:
            msg = f"discover_optical_node: {vendor} {platform}"
            raise UnsupportedPlatformError(msg)


def get_optical_node_client(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
) -> FlexilsClient | G30Client | G42Client:
    """Return the client to reach the given Optical Node, based on its vendor.

    Args:
        optical_node_block: The Optical Node block (any lifecycle variant).

    Returns:
        The client to reach the node.

    Raises:
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return get_flex_client(_as_flexils_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return get_g30_client(optical_node_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            return get_g42_client(optical_node_block)
        case _:
            msg = f"get_optical_node_client: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def retrieve_software_version(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> str:
    """Retrieve the software version of the node from the device, dispatching on the vendor.

    Args:
        optical_node_block: The Optical Node block (any lifecycle variant).

    Returns:
        The software version of the node.

    Raises:
        ValueError: If the software version cannot be retrieved from the node.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.software_version(_as_flexils_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.software_version(_as_g30_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GX_G42):
            return gx_g42.software_version(_as_g42_block(optical_node_block))
        case _:
            msg = f"retrieve_software_version: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def retrieve_optical_node_role_and_software_version(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
) -> tuple[OpticalNodeRole, str]:
    """Retrieve the node role and software version of the node, dispatching on the vendor.

    Args:
        optical_node_block: The Optical Node block (any lifecycle variant).

    Returns:
        A tuple of the node role and the software version.

    Raises:
        ValueError: If the role or the version cannot be retrieved from the node.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.role_and_version(_as_flexils_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            g30_block = _as_g30_block(optical_node_block)
            return groove_g30.role(g30_block), groove_g30.software_version(g30_block)
        case (Vendor.NOKIA, Platform.GX_G42):
            g42_block = _as_g42_block(optical_node_block)
            return gx_g42.role(g42_block), gx_g42.software_version(g42_block)
        case _:
            msg = f"retrieve_optical_node_role_and_software_version: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def retrieve_omses_terminating_on_device(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
) -> list[dict[str, Any]]:
    """Retrieve all the Optical Muxed Sections terminating on a given Optical Node.

    Args:
        optical_node_block: The Optical Node block for which Optical Muxed Sections are to be retrieved.

    Returns:
        A list of dictionaries containing information about the Optical Muxed Sections.
        Empty for the vendors that do not support this retrieval.

    Raises:
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.retrieve_omses(_as_flexils_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GROOVE_G30) | (Vendor.NOKIA, Platform.GX_G42):
            return []
        case _:
            msg = f"retrieve_omses_terminating_on_device: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def retrieve_ports_spectral_occupations(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
) -> dict[str, list[tuple[int, int]]]:
    """Retrieve the spectral occupations of the ports of a given Optical Node.

    Args:
        optical_node_block: The Optical Node block for which port spectral occupations are to be retrieved.

    Returns:
        A dictionary where keys are port names and values are lists of spectral occupations.
        Empty for the vendors that do not support this retrieval: the Groove G30 and the
        GX G42 never report spectral occupation, so their whole spectrum is always free.
        The empty mapping is the truthful answer for those platforms, not "unknown" —
        callers read it as "nothing is occupied" and clear the passbands accordingly.

    Raises:
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.retrieve_ports_spectral_occupations(_as_flexils_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GROOVE_G30) | (Vendor.NOKIA, Platform.GX_G42):
            return {}
        case _:
            msg = f"retrieve_ports_spectral_occupations: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)
