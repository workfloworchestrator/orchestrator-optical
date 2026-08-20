"""Product Blocks of OLS Add/Drop Optical Ports."""

from typing import Literal

from pydantic import Field

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
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

    optical_port_role: Literal[OpticalPortRole.OLS_ADD_DROP] = OpticalPortRole.OLS_ADD_DROP
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_passbands: OpticalPassbandList = Field(default_factory=list)
    optical_port_host_node: AbstractOpticalNodeBlockInactive


class OlsAddDropPortBlockProvisioning(
    OlsAddDropPortBlockInactive, AbstractOpticalOlsPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_ADD_DROP] = OpticalPortRole.OLS_ADD_DROP
    optical_port_name: str
    optical_port_description: str | None
    optical_passbands: OpticalPassbandList
    optical_port_host_node: AbstractOpticalNodeBlockProvisioning


class OlsAddDropPortBlock(
    OlsAddDropPortBlockProvisioning, AbstractOpticalOlsPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_ADD_DROP] = OpticalPortRole.OLS_ADD_DROP
    optical_port_name: str
    optical_port_description: str | None
    optical_passbands: OpticalPassbandList
    optical_port_host_node: AbstractOpticalNodeBlock
