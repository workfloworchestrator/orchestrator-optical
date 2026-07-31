from __future__ import annotations

from typing import TYPE_CHECKING

from ..data_navigators._base import TemplateRegistry  # noqa: TID252

if TYPE_CHECKING:
    from ..data_models import ne  # noqa: TID252


@TemplateRegistry.register("InterfaceListNode")
def interface_list_template(
    *,
    lo_ip: str | None,
    lo_name: str | None,
    eth1_ip: str | None,
    eth1_prefix_length: int | None,
    osc_names: list[str] | None,
) -> list[ne.InterfaceItem]:
    from ..data_models.ne import InterfaceItem  # noqa: PLC0415, TID252

    interfaces = []

    # Loopback
    if lo_ip:
        interfaces.append(
            InterfaceItem.model_validate(
                {
                    "if-name": lo_name,
                    "if-description": "",
                    "if-type": "softwareLoopback",
                    "admin-status": "up",
                    "alias-name": f"interface-{lo_name}",
                    "ipv4": {
                        "ipv4-forwarding": True,
                        "mtu": 1500,
                        "ipv4-address-assignment-method": "static",
                        "ip-address": {"ip": lo_ip, "prefix-length": 32},
                    },
                }
            )
        )

    # eth1
    if eth1_ip:
        interfaces.append(
            InterfaceItem.model_validate(
                {
                    "if-name": "eth1",
                    "if-description": "Local Craft Interface",
                    "if-type": "ethernetCsmacd",
                    "admin-status": "up",
                    "alias-name": "interface-eth1",
                    "ipv4": {
                        "ipv4-forwarding": True,
                        "proxy-arp": False,
                        "mtu": 1500,
                        "ipv4-address-assignment-method": "static",
                        "ip-address": {"ip": eth1_ip, "prefix-length": eth1_prefix_length},
                    },
                    "ethernet": {
                        "auto-negotiation": "enabled",
                        "duplex-mode": "full",
                        "ethernet-rate": "max-rate",
                        "flow-control": "tx-rx",
                        "eth-resource-ref": "/ne:ne/shelf[shelf-id='1']/slot[slot-id='12']/card/port[port-id='1']/eth1g",
                        "alias-name": "ethernet-eth1",
                    },
                    "ipv6": {"enabled": False, "mtu": 1500, "ipv6-address-assignment-method": "autoconfig"},
                }
            )
        )

    # OSCX
    for osc_name in osc_names or []:
        chassis_id = osc_name.split("/")[0]
        intf_name = f"intf_oscx{chassis_id}"

        interfaces.append(
            InterfaceItem.model_validate(
                {
                    "if-name": intf_name,
                    "if-description": "",
                    "if-type": "oscx",
                    "admin-status": "up",
                    "alias-name": f"interface-{intf_name}",
                    "ipv4": {
                        "ipv4-forwarding": True,
                        "mtu": 1500,
                        "ipv4-address-assignment-method": "static",
                        "ip-address": {"ip": lo_ip, "prefix-length": 32},
                        "ip-unnumbered": {
                            "unnum-enabled": True,
                            "parent-interface": f"/ne:ne/system/networking/interface[if-name='{lo_name}']",
                        },
                    },
                    "oscx": {
                        "oscx-channel": "1",
                        "oscx-resource-ref": f"/ne:ne/services/optical-interfaces/osc[osc-name='{osc_name}']",
                        "alias-name": "",
                    },
                }
            )
        )

    return interfaces


@TemplateRegistry.register("RoutingProtocolListNode")
def routing_protocol_list_template(
    *,
    ospf_router_id: str | None,
    is_ospf_asbr: bool | None,
    oscx_intf_names: list[str] | None,
    eth1_intf_name: str | None,
    eth1_default_gateway: str | None,
    eth1_default_out_intf_name: str | None,
) -> list[ne.RoutingProtocolItem]:
    from ..data_models.ne import RoutingProtocolItem  # noqa: PLC0415, TID252

    if oscx_intf_names is None:
        oscx_intf_names = []

    # eBGP always off
    protocols = [
        {
            "rtp-type": "ebgp",
            "rtp-name": "ebgp-route",
            "description": "Ebgp routing protocol",
            "bgp": {
                "admin-status": "down",
                "alias-name": "bgp-ebgp/ebgp-route",
                "as": 1,
                "router-id": "169.254.0.1",
            },
        }
    ]

    # OSPF
    if ospf_router_id:
        ospf = {
            "rtp-type": "ospfv2",
            "rtp-name": "ospfv2-route",
            "description": "Ospfv2 routing protocol",
            "ospf": {
                "router-id": ospf_router_id,
                "description": "Ospfv2 routing protocol",
                "ospf-asbr": is_ospf_asbr,
                "admin-status": "up",
                "alias-name": "ospf-ospfv2/ospfv2-route",
                "ospf-area": [
                    {
                        "ospf-area-id": "0.0.0.0",  # noqa: S104
                        "ospf-area-type": "normal",
                        "admin-status": "up",
                        "alias-name": "ospf-area-ospfv2/ospfv2-route/0.0.0.0",
                        "ospf-interface": [],
                    }
                ],
            },
        }

        # Add interfaces in OSPF area
        for name in oscx_intf_names:
            ospf["ospf"]["ospf-area"][0]["ospf-interface"].append(
                {
                    "ospf-if-name": name,
                    "ospf-linkpf": "default",
                    "dr-priority": 1,
                    "ospf-cost": 20,
                    "ospf-if-routing": "active",
                }
            )

        if eth1_intf_name:
            ospf["ospf"]["ospf-area"][0]["ospf-interface"].append(
                {
                    "ospf-if-name": eth1_intf_name,
                    "ospf-linkpf": "default",
                    "dr-priority": 1,
                    "ospf-cost": 10,
                    "ospf-if-routing": "active",
                }
            )

        protocols.append(ospf)

    # Static last resort
    if eth1_intf_name:
        protocols.append(
            {
                "rtp-type": "static",
                "rtp-name": "static-route",
                "description": "Static routing pseudo-protocol",
                "static-route": [
                    {
                        "destination-prefix": "0.0.0.0/0",
                        "description": "",
                        "advertised": False,
                        "next-hop": [
                            {
                                "index": "1",
                                "outgoing-interface": f"/ne:ne/system/networking/interface[if-name='{eth1_default_out_intf_name}']",  # noqa: E501
                                "next-hop-address": eth1_default_gateway,
                                "metric": 0,
                            }
                        ],
                    }
                ],
            }
        )

    return [RoutingProtocolItem(**p) for p in protocols]
