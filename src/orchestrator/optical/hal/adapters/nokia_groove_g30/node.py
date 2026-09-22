"""Nokia Groove G30 node operations: software version and role."""

from structlog import get_logger

from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import get_g30_client
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30BlockProvisioning
from orchestrator.optical.services.nokia.g30.data_models.ne import SwloadStateEnum

logger = get_logger(__name__)


def software_version(node: NokiaGrooveG30BlockProvisioning) -> str:
    """Retrieve the software version of a Groove G30 node from the device via RESTCONF.

    Args:
        node: The Groove G30 node block.

    Returns:
        The software version of the node.

    Raises:
        ValueError: If no firmware version can be found on the node.
    """
    g30 = get_g30_client(node)
    current_fw = g30.data.ne_ne.system.sw_management.softwareload.retrieve(content="all", depth=2)

    version = next(
        (item.swload_version for item in current_fw if item.swload_state == SwloadStateEnum.ACTIVE),
        None,
    )
    if version is None:
        msg = "No current firmware version found on the Groove G30 node"
        raise ValueError(msg)
    logger.info("Retrieved Groove G30 software version", g30_url=g30.url, software_version=version)
    return version


def role(node: NokiaGrooveG30BlockProvisioning) -> OpticalNodeRole:
    """Determine the node role of a Groove G30 node from its inventory.

    The node is a transponder unless it carries an OCC2 (Optical carrier card
    of type II) in its inventory, in which case it also acts as an xOADM.

    Args:
        node: The Groove G30 node block.

    Returns:
        The OpticalNodeRole of the node.
    """
    g30 = get_g30_client(node)
    inventory = g30.data.ne_ne.inventory_data.inventory.retrieve(depth=2)
    has_occ2 = any(item.module_type == "OCC2" for item in inventory)
    return OpticalNodeRole.TRANSPONDER_XOADM if has_occ2 else OpticalNodeRole.TRANSPONDER
