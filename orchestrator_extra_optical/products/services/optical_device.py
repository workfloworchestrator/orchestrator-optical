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

import heapq
import logging
from math import cos, radians, sin
from random import sample
from typing import Any, ClassVar

from orchestrator.domain.base import ProductBlockModel
from pydantic_forms.types import UUIDstr

from orchestrator_extra_optical.products.product_blocks.optical_device import (
    OpticalDeviceBlock,
    OpticalDeviceBlockProvisioning,
    Platform,
    Vendor,
)
from orchestrator_extra_optical.services.infinera import FlexilsClient, G30Client, G42Client, tnms_client
from orchestrator_extra_optical.utils.attributedispatch import (
    attribute_dispatch_base,
    attributedispatch,
)
from orchestrator_extra_optical.utils.custom_types.frequencies import available_to_used_passbands
from orchestrator_extra_optical.utils.custom_types.ip_address import IPAddress
from orchestrator_extra_optical.workflows.shared import subscription_instances_by_block_type_and_resource_value

logger = logging.getLogger(__name__)


class FlexilsGneProvider:
    _gne_ip_by_sne: ClassVar[dict[UUIDstr, IPAddress]] = {}
    _tid_ip_xyz_of_gnes: ClassVar[list[tuple[str, IPAddress, tuple[float, float, float]]]] = []

    @classmethod
    def _initialize_cache(cls):
        """Populates the cache if empty."""
        sub_instances = subscription_instances_by_block_type_and_resource_value(
            product_block_type="OpticalDevice",
            resource_type="platform",
            resource_value=Platform.FlexILS,
        )

        cls._gne_ip_by_sne = {}
        cls._tid_ip_xyz_of_gnes = []
        for si in sub_instances:
            dev = OpticalDeviceBlock.from_db(si.subscription_instance_id)
            if dev.mngmt_ip and dev.pop.latitude and dev.pop.longitude:
                lat = radians(float(dev.pop.latitude))
                lon = radians(float(dev.pop.longitude))

                cos_lat = cos(lat)
                x = cos_lat * cos(lon)
                y = cos_lat * sin(lon)
                z = sin(lat)

                vector = (x, y, z)
                cls._tid_ip_xyz_of_gnes.append((dev.fqdn.removesuffix(".garr.net"), dev.mngmt_ip, vector))

        msg = f"Initialized FlexilsGneProvider cache with GNEs: {cls._tid_ip_xyz_of_gnes}"
        logger.debug(msg)

    @classmethod
    def find_closest_gne_ip(cls, ne: OpticalDeviceBlock) -> IPAddress:
        if not cls._tid_ip_xyz_of_gnes:
            cls._initialize_cache()

        ne_id = str(ne.subscription_instance_id)
        logger.debug("Finding closest GNE for NE %s", ne_id)
        logger.debug("Cache: %s", cls._gne_ip_by_sne)

        if ne_id in cls._gne_ip_by_sne:
            return cls._gne_ip_by_sne[ne_id]

        if not ne.pop.latitude or not ne.pop.longitude:
            logger.warning("Pop latitude or longitude is missing for NE %s", ne.pop.code)
            random_ip_tid_xyz_of_gnes = sample(cls._tid_ip_xyz_of_gnes, min(len(cls._tid_ip_xyz_of_gnes), 7))
            nearest_gne_ips = [(tid, ip) for tid, ip, _ in random_ip_tid_xyz_of_gnes]

        else:
            lat = radians(float(ne.pop.latitude))
            lon = radians(float(ne.pop.longitude))

            cos_lat = cos(lat)
            x = cos_lat * cos(lon)
            y = cos_lat * sin(lon)
            z = sin(lat)

            target_vector = (x, y, z)

            def dot(vector):
                return target_vector[0] * vector[0] + target_vector[1] * vector[1] + target_vector[2] * vector[2]

            dot_products = [(tid, ip, dot(vector)) for tid, ip, vector in cls._tid_ip_xyz_of_gnes]
            nearest_gne_ips = [(tid, ip) for tid, ip, _ in heapq.nlargest(7, dot_products, key=lambda x: x[2])]

        target_aid = ne.fqdn.removesuffix(".garr.net")
        for gne_tid, gne_ip in nearest_gne_ips:
            try:
                flex = FlexilsClient.get_instance(tid=gne_tid, gne_ip=gne_ip, timeout=10)
                response = flex.rtrv_toponode()
                parsed_data = response.parsed_data
                if any(target_aid in node["NENAME"] for node in parsed_data):
                    cls._gne_ip_by_sne[ne_id] = gne_ip
                    return gne_ip
            except Exception:  # noqa: BLE001
                msg = f"Failed to query GNE {gne_ip} for {target_aid}"
                logger.warning(msg, exc_info=True)
                continue

        msg = f"No GNE found for NE {ne.fqdn} within these nodes: {nearest_gne_ips}"
        raise UserWarning(msg)


@attributedispatch("platform")
def get_optical_device_client(optical_device: OpticalDeviceBlock) -> FlexilsClient | G30Client | G42Client:
    return attribute_dispatch_base(get_optical_device_client, "platform", optical_device.platform)


@get_optical_device_client.register(Platform.FlexILS)
def _(optical_device: OpticalDeviceBlock) -> FlexilsClient:
    tid = optical_device.fqdn.removesuffix(".garr.net")
    gne_ip = optical_device.mngmt_ip or FlexilsGneProvider.find_closest_gne_ip(optical_device)
    return FlexilsClient.get_instance(tid=tid, gne_ip=gne_ip)


@get_optical_device_client.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock) -> G30Client:
    lo_ip = optical_device.lo_ip
    mngmt_ip = optical_device.mngmt_ip
    return G30Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)


@get_optical_device_client.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock) -> G42Client:
    lo_ip = optical_device.lo_ip
    mngmt_ip = optical_device.mngmt_ip
    return G42Client(lo_ip=lo_ip, mngmt_ip=mngmt_ip)


@attributedispatch("vendor")
def get_nms_uuid(optical_device: ProductBlockModel) -> UUIDstr:
    """Retrieve the uuid of an optical device from its Network Management System (generic function).

    Specific implementations of this generic function MUST specify the *vendor* they work on.

    Args:
        optical_device: Optical device of which the NMS uuid is to be retrieved

    Returns:
        The UUID of the optical device in its Network Management System

    Raises:
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be
            part of the error message.

    """
    return attribute_dispatch_base(get_nms_uuid, "vendor", optical_device.vendor)


@get_nms_uuid.register(Vendor.Infinera)
def _(optical_device: OpticalDeviceBlockProvisioning) -> UUIDstr:
    filter_string = optical_device.fqdn.removesuffix(".garr.net")
    devices = tnms_client.data.equipment.devices.retrieve(fields=["name", "uuid"])
    devices = [device for device in devices if device["name"][0]["value"] == filter_string]
    if len(devices) == 1:
        return devices[0]["uuid"]
    msg = f"Found {len(devices)} devices with name {filter_string}. Expected 1."
    raise ValueError(msg)


@attributedispatch("platform")
def retrieve_omses_terminating_on_device(
    optical_device: OpticalDeviceBlock,
) -> list[dict[str, Any]]:
    """Retrieve all the Optical Muxed Sections terminating on a given Optical Device.

    This function acts as a generic dispatcher based on the platform of the optical device.
    Specific implementations of this function must specify the platform they work on.

    Args:
        optical_device: The OpticalDeviceBlock for which Optical Muxed Sections are to be retrieved.

    Returns:
        A list of dictionaries containing information about the Optical Muxed Sections.

    Raises:
        TypeError: If a specific implementation could not be found for the given platform.

    Example return:
        [
            {
                'local_port': '1-A-2-L1',
                'remote_port': '1-A-1-L1',
                'local_device': 'flex.aa00.garr.net',
                'remote_device': 'flex.zz99.garr.net',
                'available_passbands': [
                    [191362500, 191375000],
                ]
            },
            {
                'local_port': '1-A-1-L1',
                'remote_port': '1-A-2-L1',
                'local_device': 'flex.aa00.garr.net',
                'remote_device': 'flex.bb11.garr.net',
                'available_passbands': [
                    [196062500, 196075000],
                    [196112500, 196125000],
                ]
            }
        ]
    """
    return attribute_dispatch_base(retrieve_omses_terminating_on_device, "platform", optical_device.platform)


@retrieve_omses_terminating_on_device.register(Platform.FlexILS)
def _(optical_device: OpticalDeviceBlock) -> list[dict[str, Any]]:
    flex = get_optical_device_client(optical_device)
    response = flex.rtrv_otelink()
    omses = []
    for otelink in response.parsed_data:
        if otelink["REACHSCOPE"] == "Local":
            local_device, local_port = otelink["AID"].split("-", 1)
            remote_device, remote_port = otelink["MATETELINK"].split("-", 1)
            available_passbands = [[int(x) for x in inner_list] for inner_list in otelink["AVAILFREQRANGELIST"]]
            local_device = f"{local_device}.garr.net"
            remote_device = f"{remote_device}.garr.net"
            omses.append(
                {
                    "local_port": local_port,
                    "remote_port": remote_port,
                    "local_device": local_device,
                    "remote_device": remote_device,
                    "available_passbands": available_passbands,
                }
            )


@attributedispatch("platform")
def retrieve_ports_spectral_occupations(
    optical_device: OpticalDeviceBlock,
) -> dict[str, list[list[int]]]:
    """Retrieve the spectral occupations of ports on a given Optical Device.

    This function acts as a generic dispatcher based on the platform of the optical device.
    Specific implementations of this function must specify the platform they work on.

    Args:
        optical_device: The OpticalDeviceBlock for which port spectral occupations are to be retrieved.

    Returns:
        A dictionary where keys are port names and values are lists of spectral occupations.

    Raises:
        TypeError: If a specific implementation could not be found for the given platform.

    Example return:
        {
            '1-A-2-L1': [
                [191362500, 191375000],
            ],
            '1-A-1-L1': [
                [196062500, 196075000],
                [196112500, 196125000],
            ]
        }
    """
    return attribute_dispatch_base(retrieve_ports_spectral_occupations, "platform", optical_device.platform)


@retrieve_ports_spectral_occupations.register(Platform.FlexILS)
def _(optical_device: OpticalDeviceBlock) -> dict[str, list[list[int]]]:
    spectral_occupations = {}
    flex = get_optical_device_client(optical_device)
    response = flex.rtrv_otelink()
    for otelink in response.parsed_data:
        if otelink["REACHSCOPE"] == "Local":
            _, local_port = otelink["AID"].split("-", 1)
            if not isinstance(otelink["AVAILFREQRANGELIST"][0], list):
                otelink["AVAILFREQRANGELIST"] = [otelink["AVAILFREQRANGELIST"]]
            available_passbands = [[int(x) for x in inner_list] for inner_list in otelink["AVAILFREQRANGELIST"]]
            spectral_occupations[local_port] = available_to_used_passbands(available_passbands)
    return spectral_occupations


@retrieve_ports_spectral_occupations.register(Platform.Groove_G30)
def _(optical_device: OpticalDeviceBlock) -> dict[str, list[list[int]]]:  # noqa: ARG001
    return {}


@retrieve_ports_spectral_occupations.register(Platform.GX_G42)
def _(optical_device: OpticalDeviceBlock) -> dict[str, list[list[int]]]:  # noqa: ARG001
    return {}
