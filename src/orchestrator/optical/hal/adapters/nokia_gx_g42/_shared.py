"""Device-level, cross-area helpers shared by the Nokia GX G42 adapter modules."""

from orchestrator.optical.products.product_blocks.optical_node._abstracts import _AbstractOpticalNodeBlockProvisioning
from orchestrator.optical.services.nokia import G42Client


def get_g42_client(optical_node_block: _AbstractOpticalNodeBlockProvisioning) -> G42Client:
    """Return a RESTCONF client to reach the given Nokia GX G42 node.

    Args:
        optical_node_block: The Nokia GX G42 node block (any lifecycle variant).

    Returns:
        A GX G42 RESTCONF client.
    """
    return G42Client(
        loopback_ip=str(optical_node_block.management.optical_module_node_dcn_loopback_ip or "") or None,
        management_ip=str(optical_node_block.management.optical_module_node_dcn_interface_ip or "") or None,
    )
