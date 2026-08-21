"""Core block of Optical Node Product Blocks."""

from typing import Annotated

from annotated_types import Len
from pydantic import Field, model_validator
from pydantic_forms.types import strEnum

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress

IpAddressList = Annotated[
    list[IPAddress], Len(min_length=0, max_length=10), "List of the management IP addresses of the device."
]

class Vendor(strEnum):
    """Vendors of network nodes."""

    NOKIA = "Nokia"
    CISCO = "Cisco"
    JUNIPER = "Juniper"
    ADVA = "ADVA"

class Platform(strEnum):
    """Platforms of network nodes."""

    SR = "SR"
    NCS = "NCS"
    MX = "MX"
    PTX = "PTX"
    FLEXILS = "FLEXILS"
    GROOVE_G30 = "GROOVE G30"
    GX_G42 = "GX G42"


class OpticalModuleNodeManagementBlockInactive(ProductBlockModel, product_block_name="OpticalModuleNodeManagementBlock"):
    """."""
    optical_module_node_vendor: Vendor | None = None
    optical_module_node_platform: Platform | None = None
    optical_module_node_software_version: str | None = None
    optical_module_node_fqdn: Fqdn | None = None
    optical_module_node_management_ips: IpAddressList = Field(default_factory=list)


class OpticalModuleNodeManagementBlockProvisioning(OpticalModuleNodeManagementBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """."""
    optical_module_node_vendor: Vendor
    optical_module_node_platform: Platform
    optical_module_node_software_version: str | None
    optical_module_node_fqdn: Fqdn
    optical_module_node_management_ips: IpAddressList

class OpticalModuleNodeManagementBlock(OpticalModuleNodeManagementBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """."""
    optical_module_node_vendor: Vendor
    optical_module_node_platform: Platform
    optical_module_node_software_version: str
    optical_module_node_fqdn: Fqdn
    optical_module_node_management_ips: IpAddressList
