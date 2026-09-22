"""Nokia GX G42 node-level HAL operations."""

from structlog import get_logger

from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import get_g42_client
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import NokiaGxG42BlockProvisioning

logger = get_logger(__name__)


def software_version(node: NokiaGxG42BlockProvisioning) -> str:
    """Retrieve the software version of a GX G42 node from the device via RESTCONF.

    Reads the active software load directly at
    ``/restconf/data/ioa-network-element:ne/system/sw-management/software-load=active``.

    Args:
        node: The GX G42 node block.

    Returns:
        The software version of the node.

    Raises:
        ValueError: If the active software load has no version.
    """
    g42 = get_g42_client(node)
    active = g42.data.ne.system.sw_management.software_load("active").retrieve(depth=2)
    version = active.swload_version
    if version is None:
        msg = f"No current firmware version found on GX G42 node {g42.url}"
        raise ValueError(msg)
    logger.info("Retrieved GX G42 software version", g42_url=g42.url, software_version=version)
    return version


def role(node: NokiaGxG42BlockProvisioning) -> OpticalNodeRole:  # noqa: ARG001
    """Return the node role of a GX G42 node, which is always a transponder.

    Args:
        node: The GX G42 node block.

    Returns:
        The OpticalNodeRole of the node.
    """
    return OpticalNodeRole.TRANSPONDER
