"""Product Blocks of OLS Add/Drop Optical Ports."""

from pydantic import Field

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.unions import (
    OlsBlockInactiveUnion,
    OlsBlockProvisioningUnion,
    OlsBlockUnion,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalOlsPortBlock,
    AbstractOpticalOlsPortBlockInactive,
    AbstractOpticalOlsPortBlockProvisioning,
    OpticalPassbandList,
    OpticalPortRole,
)


class OlsAddDropPortBlockInactive(AbstractOpticalOlsPortBlockInactive, product_block_name="OlsAddDropPortBlock"):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: OpticalPortRole = OpticalPortRole.OLS_ADD_DROP
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_passbands: OpticalPassbandList = Field(default_factory=list)
    optical_port_host_node: OlsBlockInactiveUnion


class OlsAddDropPortBlockProvisioning(
    OlsAddDropPortBlockInactive,
    AbstractOpticalOlsPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: OpticalPortRole = OpticalPortRole.OLS_ADD_DROP
    optical_port_name: str
    optical_port_description: str | None
    optical_passbands: OpticalPassbandList
    optical_port_host_node: OlsBlockProvisioningUnion


class OlsAddDropPortBlock(
    OlsAddDropPortBlockProvisioning, AbstractOpticalOlsPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: OpticalPortRole = OpticalPortRole.OLS_ADD_DROP
    optical_port_name: str
    optical_port_description: str | None
    optical_passbands: OpticalPassbandList
    optical_port_host_node: OlsBlockUnion
