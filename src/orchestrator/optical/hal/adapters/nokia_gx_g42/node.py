"""Nokia GX G42 node-level HAL operations."""

from structlog import get_logger

from orchestrator.optical.hal._common import OpticalNodeDiscovery, _retrieve_required
from orchestrator.optical.hal.adapters.nokia_gx_g42._sdk import G42Client
from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import g42_client_for_hosts, get_g42_client
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning

logger = get_logger(__name__)


def software_version(node: NokiaGxG42BlockProvisioning) -> str:
    """Retrieve the software version of a GX G42 node from the device via NETCONF.

    Reads the active software load directly at
    ``ioa-network-element:ne/system/sw-management/software-load[name=active]``.

    Args:
        node: The GX G42 node block.

    Returns:
        The software version of the node.

    Raises:
        ValueError: If the active software load has no version.
    """
    return _software_version(get_g42_client(node))


def _software_version(g42: G42Client) -> str:
    """Read the active software version over an open session (see :func:`software_version`)."""
    active = _retrieve_required(
        g42.data.ioa_network_element_ne.system.sw_management.software_load("active").retrieve, depth=2
    )
    version = active.swload_version
    if version is None:
        msg = f"No current firmware version found on GX G42 node {g42.host}"
        raise ValueError(msg)
    logger.info("Retrieved GX G42 software version", g42_host=g42.host, software_version=version)
    return version


def role(node: NokiaGxG42BlockProvisioning) -> OpticalNodeRole:  # noqa: ARG001
    """Return the node role of a GX G42 node, which is always a transponder.

    Args:
        node: The GX G42 node block.

    Returns:
        The OpticalNodeRole of the node.
    """
    return OpticalNodeRole.TRANSPONDER


def discover(hosts: tuple[str, ...]) -> OpticalNodeDiscovery:
    """Read the name, role and software version of the GX G42 reachable at one of ``hosts``.

    This is the discovery of a node that has no block yet (create form): the name is the
    ``ne-name`` configured on the device, the role and the version are read as for a
    modelled node (see :func:`role` and :func:`software_version`).

    Args:
        hosts: The management IPs to try, in order.

    Returns:
        The discovered node properties; the name is ``None`` when the device has none.

    Raises:
        ValueError: If the node reports no data or no active software version.
        ExceptionGroup: If no host is reachable.
    """
    g42 = g42_client_for_hosts(hosts)
    ne = _retrieve_required(g42.data.ioa_network_element_ne.retrieve, depth=2, content="config")
    return OpticalNodeDiscovery(
        name=(ne.ne_name or "").strip() or None,
        role=OpticalNodeRole.TRANSPONDER,
        software_version=_software_version(g42),
    )
