"""Product Blocks of Nokia Groove G30 Optical Nodes."""

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import (
    AbstractOpticalLocationBlock,
    AbstractOpticalLocationBlockInactive,
    AbstractOpticalLocationBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
    OpticalNodeRole,
)
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress


class NokiaGrooveG30BlockInactive(AbstractOpticalNodeBlockInactive, product_block_name="NokiaGrooveG30Block"):
    """Product Block of a Nokia Groove G30 Optical Node that is inactive."""

    optical_node_role: OpticalNodeRole | None = None
    optical_node_software_version: str | None = None
    pqdn: Pqdn | None = None
    optical_management_ip: IPAddress | None = None
    optical_loopback_ip: IPAddress | None = None
    location: AbstractOpticalLocationBlockInactive | None = None


class NokiaGrooveG30BlockProvisioning(
    NokiaGrooveG30BlockInactive, AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Product Block of a Nokia Groove G30 Optical Node that is provisioning."""

    optical_node_role: OpticalNodeRole
    optical_node_software_version: str | None
    pqdn: Pqdn
    optical_management_ip: IPAddress | None = None
    optical_loopback_ip: IPAddress | None = None
    location: AbstractOpticalLocationBlockProvisioning


class NokiaGrooveG30Block(
    NokiaGrooveG30BlockProvisioning, AbstractOpticalNodeBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Product Block of a Nokia Groove G30 Optical Node that is active."""

    optical_node_role: OpticalNodeRole
    optical_node_software_version: str
    pqdn: Pqdn
    optical_management_ip: IPAddress | None = None
    optical_loopback_ip: IPAddress | None = None
    location: AbstractOpticalLocationBlock
