"""Nokia Groove G30 node operations: software version and role."""

from structlog import get_logger

from orchestrator.optical.hal._common import OpticalNodeDiscovery, _retrieve_required
from orchestrator.optical.hal.adapters.nokia_groove_g30._sdk import G30Client
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import (
    g30_client_for_hosts,
    g30_modules,
    g30_modules_of_client,
    g30_node_functions,
    g30_role,
    get_g30_client,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30BlockProvisioning

logger = get_logger(__name__)


def software_version(node: NokiaGrooveG30BlockProvisioning) -> str:
    """Retrieve the software version of a Groove G30 node from the device via NETCONF.

    Args:
        node: The Groove G30 node block.

    Returns:
        The software version of the node.

    Raises:
        ValueError: If no firmware version can be found on the node.
    """
    return _software_version(get_g30_client(node))


def _software_version(g30: G30Client) -> str:
    """Read the active software version over an open session (see :func:`software_version`)."""
    current_fw = g30.data.ne_ne.system.sw_management.softwareload.retrieve(content="all", depth=2)

    version = next(
        (item.swload_version for item in current_fw if item.swload_state == "Active"),
        None,
    )
    if version is None:
        msg = "No current firmware version found on the Groove G30 node"
        raise ValueError(msg)
    logger.info("Retrieved Groove G30 software version", g30_host=g30.host, software_version=version)
    return version


def role(node: NokiaGrooveG30BlockProvisioning) -> OpticalNodeRole:
    """Determine the node role of a Groove G30 node from its installed cards.

    A Groove G30 is a transponder, an amplifier, a FOADM or a ROADM depending on the
    cards it carries: a wavelength selector (WSS) makes it a ROADM, a colorless or
    fixed add/drop makes it a FOADM, amplifiers alone make it an amplifier, and the
    presence of a transponder card is what distinguishes the transponder flavours of
    the ROADM and FOADM from their bare counterparts. See
    :func:`orchestrator.optical.hal.adapters.nokia_groove_g30._shared.g30_role` for the
    full mapping.

    Args:
        node: The Groove G30 node block.

    Returns:
        The OpticalNodeRole of the node.

    Raises:
        ValueError: If the node has no role-relevant optical card installed.
    """
    functions = g30_node_functions(g30_modules(node))
    return g30_role(functions, node.management.optical_module_node_name)


def discover(hosts: tuple[str, ...]) -> OpticalNodeDiscovery:
    """Read the name, role and software version of the Groove G30 reachable at one of ``hosts``.

    This is the discovery of a node that has no block yet (create form): the name is the
    ``ne-name`` configured on the device, the role and the version are read as for a
    modelled node (see :func:`role` and :func:`software_version`).

    Args:
        hosts: The management IPs to try, in order.

    Returns:
        The discovered node properties; the name is ``None`` when the device has none.

    Raises:
        ValueError: If the node reports no data, no optical card or no active software load.
        ExceptionGroup: If no host is reachable.
    """
    g30 = g30_client_for_hosts(hosts)
    ne = _retrieve_required(g30.data.ne_ne.retrieve, depth=2, content="config")
    name = (ne.ne_name or "").strip() or None
    return OpticalNodeDiscovery(
        name=name,
        role=g30_role(g30_node_functions(g30_modules_of_client(g30)), name or g30.host),
        software_version=_software_version(g30),
    )
