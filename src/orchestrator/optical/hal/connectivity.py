"""Connectivity-area HAL: the internal routes of an Optical Node, from add/drop port to degree.

The path engine asks the source and destination nodes of an optical path which OLS line
ports (degrees) the selected add/drop port can be connected to, and which frequencies
are already used on each of those internal routes. The answer is read live from the
device (internal patches, card types and provisioned cross-connections) and returned as
the vendor-neutral :class:`IntraNodeEdge` contract.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from orchestrator.optical.hal._common import (
    IntraNodeEdge,
    LazyAdapter,
    UnsupportedPlatformError,
    _as_flexils_block,
    _as_g30_block,
    _vendor_platform,
)
from orchestrator.optical.hal.adapters.nokia_groove_g30.naming import g30_shelf_of_port
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor

if TYPE_CHECKING:
    from orchestrator.optical.hal.adapters.nokia_flexils import connectivity as flexils
    from orchestrator.optical.hal.adapters.nokia_groove_g30 import connectivity as groove_g30
else:
    flexils = LazyAdapter("orchestrator.optical.hal.adapters.nokia_flexils.connectivity")
    groove_g30 = LazyAdapter("orchestrator.optical.hal.adapters.nokia_groove_g30.connectivity")

__all__ = ["IntraNodeEdge", "g30_shelf_of_port", "retrieve_add_drop_connectivity"]


def retrieve_add_drop_connectivity(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    add_drop_port_name: str,
) -> list[IntraNodeEdge]:
    """Retrieve the OLS line ports an add/drop port can reach inside its node, with the occupancy.

    Args:
        optical_node_block: The Optical Node block hosting the add/drop port.
        add_drop_port_name: Device name of the add/drop port.

    Returns:
        One edge per reachable OLS line port. ``used_passbands`` holds the frequencies
        already occupied on the internal route (always empty on the Groove G30, which
        reports no spectral occupation).

    Raises:
        UnsupportedPlatformError: If the node is not an Open Line System platform.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.retrieve_add_drop_connectivity(_as_flexils_block(optical_node_block), add_drop_port_name)
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            return groove_g30.retrieve_add_drop_connectivity(_as_g30_block(optical_node_block), add_drop_port_name)
        case _:
            msg = f"retrieve_add_drop_connectivity: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)
