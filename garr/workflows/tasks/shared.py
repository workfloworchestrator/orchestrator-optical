# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import re
import time
from typing import Annotated

from jnpr.junos import Device
from orchestrator.forms.validators import Choice, choice_list
from pydantic import Field, TypeAdapter
from structlog import get_logger

from services import netbox
from utils.custom_types.ip_address import IPAddress

logger = get_logger(__name__)


def retrieve_all_router_from_netbox_selector() -> type[list[Choice]]:
    """Retrieves all routers from NetBox for selection in the form."""
    routers = netbox.api.ipam.ip_addresses.filter(parent="10.30.0.0/16")
    choices = {}
    for r in routers:
        ip = r.address.split("/")[0]
        ip = TypeAdapter(IPAddress).validate_python(ip)
        choices.update({ip: f"{r.dns_name} - {ip} "})
    logger.debug("Retrieved numbers routers from NetBox", extra={"len(choices)": len(choices)})
    return Annotated[
        choice_list(
            Choice("Select the router connected to the G30", zip(choices.keys(), choices.items(), strict=False)),
            min_items=0,
            max_items=5,
            unique_items=True,
        ),
        Field(title="Select ALL routers connected to the G30"),
    ]


def retrieve_up_up_backbone_interfaces_of_routers(router_ip_addresses: list[IPAddress]) -> dict[IPAddress, list[str]]:
    if router_ip_addresses == []:
        return {}
    interfaces_by_router = {}
    for ip in router_ip_addresses:
        logger.debug("Router IP Address:", extra={"ip": ip})
        with Device(
            host=ip, user=os.getenv("JUNIPER_ROUTER_USER"), password=os.getenv("JUNIPER_ROUTER_PASSWORD")
        ) as dev:
            int_data = dev.rpc.get_interface_information(media=True)
            all_interfaces = int_data.findall("physical-interface")
            interfaces = []
            for iface in all_interfaces:
                # 3a. Interface Name
                name = iface.findtext("name", default="N/A")
                # 3b. Description and Filtering
                description = iface.findtext("description", default="")
                admin_status = iface.findtext("admin-status", default="down")
                oper_status = iface.findtext("oper-status", default="down")
                # Check if the description matches the required pattern
                if (
                    re.search(r"\[f[0-9c]+\]", description)
                    and admin_status.strip() == "up"
                    and oper_status.strip() == "up"
                ):
                    interfaces.append(name.strip())
            interfaces_by_router[ip] = interfaces

    return interfaces_by_router


def retrieve_in_out_packets_of_interfaces(
    interfaces_by_router: dict[IPAddress, list[str]],
) -> dict[str, tuple[str, str]]:
    stats = {}
    for host, interfaces in interfaces_by_router.items():
        with Device(
            host=host, user=os.getenv("JUNIPER_ROUTER_USER"), password=os.getenv("JUNIPER_ROUTER_PASSWORD")
        ) as dev:
            for iface in interfaces:
                int_data = dev.rpc.get_interface_information(interface_name=iface, media=True)
                int_data = int_data.find("physical-interface")
                mac_stats = int_data.find("ethernet-mac-statistics")
                input_packets = mac_stats.findtext("input-packets", default="0")
                output_packets = mac_stats.findtext("output-packets", default="0")

                stats[f"{host}:{iface}"] = (input_packets.strip(), output_packets.strip())

    return stats


def raise_if_no_traffic_btw_routers(interfaces_by_router: dict[IPAddress, list[str]]) -> None:
    """Check if there is traffic between routers.

    Args:
        interfaces_by_router: Dictionary of interfaces to check by router, e.g. {"10.30.0.1": ["f0/0", "f0/1"]}

    Raises:
        ValueError: If there is no traffic between routers.
    """
    stats_by_interface_t0 = retrieve_in_out_packets_of_interfaces(interfaces_by_router)
    time.sleep(4)
    stats_by_interface_t1 = retrieve_in_out_packets_of_interfaces(interfaces_by_router)

    for interface, io_t0 in stats_by_interface_t0.items():
        io_t1 = stats_by_interface_t1.get(interface, (-1, -1))
        if io_t0 == io_t1:
            msg = (
                "A backbone link is not passing traffic. I/O packets did not change after "
                f"more than 4 seconds on this JUNIPER router:interface {interface}"
            )
            raise ValueError(msg)
