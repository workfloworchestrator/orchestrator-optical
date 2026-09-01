"""Product Blocks of OLS Line Optical Ports."""

from typing import Literal

from pydantic import Field

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.unions import (
    OlsBlockInactiveUnion,
    OlsBlockProvisioningUnion,
    OlsBlockUnion,
)
from orchestrator.optical.products.product_blocks.optical_port._abstracts import (
    _AbstractOpticalOlsPortBlock,
    _AbstractOpticalOlsPortBlockInactive,
    _AbstractOpticalOlsPortBlockProvisioning,
    OpticalPassbandList,
    OpticalPortRole,
)


class OlsLinePortBlockInactive(_AbstractOpticalOlsPortBlockInactive, product_block_name="OlsLinePortBlock"):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_LINE] = OpticalPortRole.OLS_LINE
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_passbands: OpticalPassbandList = Field(default_factory=list)
    optical_port_host_node: OlsBlockInactiveUnion


class OlsLinePortBlockProvisioning(
    OlsLinePortBlockInactive, _AbstractOpticalOlsPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_LINE] = OpticalPortRole.OLS_LINE
    optical_port_name: str
    optical_port_description: str | None
    optical_passbands: OpticalPassbandList
    optical_port_host_node: OlsBlockProvisioningUnion


class OlsLinePortBlock(
    OlsLinePortBlockProvisioning, _AbstractOpticalOlsPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_LINE] = OpticalPortRole.OLS_LINE
    optical_port_name: str
    optical_port_description: str | None
    optical_passbands: OpticalPassbandList
    optical_port_host_node: OlsBlockUnion
