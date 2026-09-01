"""Nokia GX G42 node-level HAL operations."""

from structlog import get_logger

from orchestrator.optical.hal._common import OpticalNodeBlock
from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import get_g42_client
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole

logger = get_logger(__name__)


def software_version(node: OpticalNodeBlock) -> str:
    """Retrieve the software version of a GX G42 node from the device via RESTCONF.

    Args:
        node: The GX G42 node block.

    Returns:
        The software version of the node.

    Raises:
        ValueError: If no firmware version can be found on the node.
    """
    g42 = get_g42_client(node)
    chassis_items = g42.data.ne.equipment.chassis.retrieve(depth=2)
    controller = next((c for c in chassis_items if c.is_node_controller), None)
    if controller is None and chassis_items:
        controller = chassis_items[0]
    if controller is None:
        msg = "No chassis found to retrieve the software version of the GX G42 node"
        raise ValueError(msg)

    current_fw = g42.data.ne.equipment.chassis(controller.name).inventory.current_fw.retrieve(content="all", depth=2)
    version = next((item.fw_version for item in current_fw if item.fw_version is not None), None)
    if version is None:
        msg = f"No current firmware version found on GX G42 node {g42.url}"
        raise ValueError(msg)
    logger.info("Retrieved GX G42 software version", g42_url=g42.url, software_version=version)
    return version


def role(node: OpticalNodeBlock) -> OpticalNodeRole:  # noqa: ARG001
    """Return the node role of a GX G42 node, which is always a transponder.

    Args:
        node: The GX G42 node block.

    Returns:
        The OpticalNodeRole of the node.
    """
    return OpticalNodeRole.TRANSPONDER
