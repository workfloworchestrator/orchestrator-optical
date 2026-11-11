"""Device-level, cross-area helpers shared by the Nokia GX G42 adapter modules."""

from typing import Any

from orchestrator.optical.hal._common import _connect_first
from orchestrator.optical.hal.adapters.nokia_gx_g42._sdk import G42Client
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.settings import get_settings


def get_g42_client(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> G42Client:
    """Return a NETCONF client connected to the given Nokia GX G42 node.

    Every edit is committed immediately (``auto_commit``: the G42 stages edits in its
    candidate datastore), as each HAL operation is one self-contained change.

    Args:
        optical_node_block: The Nokia GX G42 node block (any lifecycle variant).

    Returns:
        A connected GX G42 NETCONF client.
    """
    settings = get_settings()
    return _connect_first(
        G42Client,
        optical_node_block,
        username=settings.g42_user,
        password=settings.g42_password,
        verify=settings.g42_verify,
        auto_commit=True,
    )


def g42_port_node(root: Any, port_name: str) -> Any:
    """Return the navigator node of a GX G42 port (``1-4-L1`` is port ``L1`` of card ``1-4``).

    Args:
        root: The data root navigator of a GX G42 client (``client.data``).
        port_name: The name of the port.
    """
    shelf_id, slot_id, port_id = port_name.split("-")
    return root.ioa_network_element_ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
