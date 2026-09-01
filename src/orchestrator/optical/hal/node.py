"""Node-area HAL: client/discovery access and the node-level retrieve/validate dispatchers.

The client factories and the FlexILS SNE discovery logic live in the per-device
adapters (see :mod:`orchestrator.optical.hal.adapters`); this module re-exports
the client factories and provides the vendor-dispatching retrieve/validate
operations, routing with ``match/case`` on the node's vendor and platform.
"""

from __future__ import annotations

from typing import Any

from structlog import get_logger

from orchestrator.optical.hal._common import (
    UnsupportedPlatformError,
    _as_flexils_block,
    _as_g30_block,
    _as_g42_block,
    _vendor_platform,
)
from orchestrator.optical.hal.adapters.nokia_flexils import node as flexils
from orchestrator.optical.hal.adapters.nokia_flexils._shared import (
    FlexilsGneProvider,
    discover_flexils_node,
    get_flex_client,
)
from orchestrator.optical.hal.adapters.nokia_groove_g30 import node as groove_g30
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import get_g30_client
from orchestrator.optical.hal.adapters.nokia_gx_g42 import node as gx_g42
from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import get_g42_client
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.services.nokia import G30Client, G42Client
from orchestrator.optical.services.nokia.flexils.client import FlexilsClient

logger = get_logger(__name__)

__all__ = [
    "FlexilsGneProvider",
    "discover_flexils_node",
    "get_flex_client",
    "get_g30_client",
    "get_g42_client",
    "get_optical_node_client",
    "retrieve_omses_terminating_on_device",
    "retrieve_optical_node_role_and_software_version",
    "retrieve_ports_spectral_occupations",
    "retrieve_software_version",
    "validate_management_network_config",
]


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
        Empty for the vendors that do not support this retrieval.

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


def validate_management_network_config(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> None:
    """Check the network configuration of a given Optical Node.

    Args:
        optical_node_block: The Optical Node block for which the network configuration is to be checked.

    Raises:
        ValueError: If the network configuration does not meet the expected criteria.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            msg = "Not yet implemented for FlexILS"
            logger.warning(msg)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            groove_g30.validate_management_network_config(_as_g30_block(optical_node_block))
        case (Vendor.NOKIA, Platform.GX_G42):
            pass
        case _:
            msg = f"validate_management_network_config: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)
