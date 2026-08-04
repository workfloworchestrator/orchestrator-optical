"""Module for Optical Port product blocks."""

from typing import Literal

from pydantic import computed_field

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_packet_node import (
    AbstractOpticalPacketNodeBlock,
    AbstractOpticalPacketNodeBlockInactive,
    AbstractOpticalPacketNodeBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalPortBlock,
    AbstractOpticalPortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    OpticalPortRole,
)


class OpticalCoherentPluggableBlockInactive(
    AbstractOpticalPortBlockInactive, product_block_name="CoherentPluggableBlock"
):
    """Base class for inactive CoherentPluggableBlock product blocks."""

    optical_port_role: Literal[OpticalPortRole.COHERENT_PLUGGABLE] = OpticalPortRole.COHERENT_PLUGGABLE
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_port_host_node: AbstractOpticalPacketNodeBlockInactive | None = None
    optical_coherent_pluggable_firmware_version: str | None = None

    @computed_field
    @property
    def optical_coherent_pluggable_part_number(self) -> str:
        """From fixed_inputs."""
        sub = SubscriptionModel.from_subscription(self.owner_subscription_id)
        return sub.optical_coherent_pluggable_part_number  # ty: ignore[unresolved-attribute] # We can't cast to the Product Type since that would cause a circular import


class OpticalCoherentPluggableBlockProvisioning(
    OpticalCoherentPluggableBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base class for provisioning CoherentPluggableBlock product blocks."""

    optical_port_role: Literal[OpticalPortRole.COHERENT_PLUGGABLE] = OpticalPortRole.COHERENT_PLUGGABLE
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: AbstractOpticalPacketNodeBlockProvisioning
    optical_coherent_pluggable_firmware_version: str


class OpticalCoherentPluggableBlock(
    OpticalCoherentPluggableBlockProvisioning, AbstractOpticalPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Base class for active CoherentPluggableBlock product blocks."""

    optical_port_role: Literal[OpticalPortRole.COHERENT_PLUGGABLE] = OpticalPortRole.COHERENT_PLUGGABLE
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: AbstractOpticalPacketNodeBlock
    optical_coherent_pluggable_firmware_version: str
