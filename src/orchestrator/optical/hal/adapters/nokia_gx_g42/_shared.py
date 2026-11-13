"""Device-level, cross-area helpers shared by the Nokia GX G42 adapter modules."""

from typing import Any

from orchestrator.optical.hal._common import _connect_first, _connect_hosts
from orchestrator.optical.hal.adapters.nokia_gx_g42._sdk import G42Client
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.settings import get_settings


def get_g42_client(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> G42Client:
    """Return a NETCONF client connected to the given Nokia GX G42 node.

    Every edit is committed immediately (``auto_commit``: the G42 stages edits in its
    candidate datastore), as each HAL operation is one self-contained change.
    Authentication is by password only: the SSH agent and the local keys are not offered
    first, as each key the node rejects costs round trips on every login.

    Args:
        optical_node_block: The Nokia GX G42 node block (any lifecycle variant).

    Returns:
        A connected GX G42 NETCONF client (shared within a device-sessions scope).
    """
    return _connect_first(G42Client, optical_node_block, **_g42_client_kwargs())


def g42_client_for_hosts(hosts: tuple[str, ...]) -> G42Client:
    """Return a NETCONF client connected to the GX G42 reachable at one of ``hosts``.

    For a node that has no block yet (discovery from a create form); see :func:`get_g42_client`.
    """
    return _connect_hosts(G42Client, hosts, **_g42_client_kwargs())


def _g42_client_kwargs() -> dict[str, Any]:
    """Return the credentials and session options of a GX G42 client, from the settings."""
    settings = get_settings()
    return {
        "username": settings.g42_user,
        "password": settings.g42_password,
        "verify": settings.g42_verify,
        "auto_commit": True,
        "allow_agent": False,
        "look_for_keys": False,
    }


def g42_port_node(root: Any, port_name: str) -> Any:
    """Return the navigator node of a GX G42 port (``1-4-L1`` is port ``L1`` of card ``1-4``).

    Args:
        root: The data root navigator of a GX G42 client (``client.data``).
        port_name: The name of the port.
    """
    shelf_id, slot_id, port_id = port_name.split("-")
    return root.ioa_network_element_ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
