"""Nokia Groove G30 node operations: software version, role and management-network validation."""

import ipaddress
import json

from structlog import get_logger

from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import get_g30_client
from orchestrator.optical.products.product_blocks.optical_node._abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import NokiaGrooveG30BlockProvisioning
from orchestrator.optical.services.nokia.g30.data_models.ne import FwStateEnum
from orchestrator.optical.utils.datadiff import compare_pydantic_objects

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
    current_fw = g30.data.ne_ne.system.sw_management.current_fw_version.retrieve(content="all", depth=2)

    version = next(
        (
            item.system_fw_version or item.device_fw_version
            for item in current_fw
            if item.fw_state == FwStateEnum.CURRENT
        ),
        None,
    )
    if version is None:
        version = next(
            (
                item.system_fw_version or item.device_fw_version
                for item in current_fw
                if item.system_fw_version is not None or item.device_fw_version is not None
            ),
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


def validate_management_network_config(optical_node_block: NokiaGrooveG30BlockProvisioning) -> None:
    """Check the network configuration of a Nokia Groove G30 node against the expected template."""
    g30 = get_g30_client(optical_node_block)
    intf_navigator = g30.data.ne_ne.system.networking.interface
    intf_config = intf_navigator.retrieve(content="config", depth=5)
    rtp_navigator = g30.data.ne_ne.system.networking.routing.routing_protocol
    rtp_config = rtp_navigator.retrieve(content="config", depth=5)
    opt_intf_config = g30.data.ne_ne.services.optical_interfaces.retrieve(content="config", depth=4)

    lo_ip = optical_node_block.management.optical_module_node_dcn_loopback_ip
    eth1_ip = optical_node_block.management.optical_module_node_dcn_interface_ip

    eth1_intf_name, eth1_gateway, is_g30_connected_to_switch, eth1_prefix_len = _get_eth1_details(eth1_ip)

    lo_intf_name = next((i.if_name for i in intf_config if i.if_type == "softwareLoopback"), "")
    osc_names = [osc.osc_name for osc in getattr(opt_intf_config, "osc", [])]
    oscx_intf_names = [f"intf_oscx{osc_name.split('/')[0]}" for osc_name in osc_names]

    desired_intf_config = intf_navigator.from_template(
        lo_ip=lo_ip,
        lo_name=lo_intf_name,
        eth1_ip=eth1_ip,
        eth1_prefix_length=eth1_prefix_len,
        osc_names=osc_names,
    )

    desired_rtp_config = rtp_navigator.from_template(
        ospf_router_id=lo_ip,
        is_ospf_asbr=is_g30_connected_to_switch,
        oscx_intf_names=oscx_intf_names,
        eth1_intf_name=eth1_intf_name,
        eth1_default_gateway=eth1_gateway,
        eth1_default_out_intf_name=eth1_intf_name,
    )

    intf_diffs = compare_pydantic_objects(expected=desired_intf_config, actual=intf_config, unique_id_keys=["if-name"])
    rtp_diffs = compare_pydantic_objects(
        expected=desired_rtp_config,
        actual=rtp_config,
        unique_id_keys=["rtp-type", "ospf-area-id", "ospf-if-name", "destination-prefix", "index"],
    )
    diffs = {
        "+++": intf_diffs["+++"] | rtp_diffs["+++"],
        "---": intf_diffs["---"] | rtp_diffs["---"],
    }

    if any(diffs.values()):
        msg = (
            f"Configuration mismatch for "
            f"{optical_node_block.management.optical_module_node_fqdn}:\n"
            f"{json.dumps(diffs, indent=2, sort_keys=True)}\n"
        )
        raise ValueError(msg)


def _get_eth1_details(eth1_ip: str | None) -> tuple[str | None, str | None, bool, int]:
    """Derive the expected eth1 interface configuration from its management IP address."""
    switch_nets = [ipaddress.ip_network(n) for n in ["10.127.0.0/16", "172.16.0.0/16"]]
    p2p_nets = [ipaddress.ip_network("10.10.0.0/16")]

    if not eth1_ip:
        return None, None, False, 0

    ip = ipaddress.ip_address(eth1_ip)

    if any(ip in net for net in switch_nets):
        prefix_len = 24
        subnet = ipaddress.ip_network(f"{eth1_ip}/{prefix_len}", strict=False)
        gateway = str(subnet.network_address + 1)
        return "eth1", gateway, True, prefix_len

    if any(ip in net for net in p2p_nets):
        prefix_len = 30
        subnet = ipaddress.ip_network(f"{eth1_ip}/{prefix_len}", strict=False)
        gateway = str(next(x for x in subnet.hosts() if x != ip))
        return "eth1", gateway, False, prefix_len

    msg = f"Invalid management IP: {eth1_ip}. Out of allowed ranges."
    raise ValueError(msg)
