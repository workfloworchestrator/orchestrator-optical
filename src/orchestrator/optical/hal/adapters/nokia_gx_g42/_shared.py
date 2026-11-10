"""Device-level, cross-area helpers shared by the Nokia GX G42 adapter modules."""

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
