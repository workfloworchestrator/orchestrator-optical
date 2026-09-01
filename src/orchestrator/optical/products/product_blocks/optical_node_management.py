"""Core block of Optical Node Product Blocks."""

from pydantic_forms.types import strEnum

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress


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
    MX204 = "MX204"
    PTX = "PTX"
    FLEXILS = "FLEXILS"
    GROOVE_G30 = "GROOVE G30"
    GX_G42 = "GX G42"


class OpticalModuleNodeManagementBlockInactive(
    ProductBlockModel, product_block_name="OpticalModuleNodeManagementBlock"
):
    """Optical Module Node Management block that is inactive."""

    optical_module_node_vendor: Vendor | None = None
    optical_module_node_platform: Platform | None = None
    optical_module_node_software_version: str | None = None
    optical_module_node_fqdn: Fqdn | None = None
    optical_module_node_dcn_loopback_ip: IPAddress | None = None
    optical_module_node_dcn_interface_ip: IPAddress | None = None


class OpticalModuleNodeManagementBlockProvisioning(
    OpticalModuleNodeManagementBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Optical Module Node Management block that is provisioning."""

    optical_module_node_vendor: Vendor
    optical_module_node_platform: Platform
    optical_module_node_software_version: str | None
    optical_module_node_fqdn: Fqdn
    optical_module_node_dcn_loopback_ip: IPAddress | None
    optical_module_node_dcn_interface_ip: IPAddress | None


class OpticalModuleNodeManagementBlock(
    OpticalModuleNodeManagementBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Optical Module Node Management block that is active."""

    optical_module_node_vendor: Vendor
    optical_module_node_platform: Platform
    optical_module_node_software_version: str
    optical_module_node_fqdn: Fqdn
    optical_module_node_dcn_loopback_ip: IPAddress | None
    optical_module_node_dcn_interface_ip: IPAddress | None
