"""Module for Optical Port product blocks."""

from typing import Literal

from orchestrator.domain import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import computed_field

from orchestrator_optical.products.product_blocks.optical_packet_node import (
    OpticalPacketNodeBlock,
    OpticalPacketNodeBlockInactive,
    OpticalPacketNodeBlockProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_port import AbstractOpticalPortBlockInactive, OpticalPortRole


class OpticalCoherentPluggableBlockInactive(
    AbstractOpticalPortBlockInactive, product_block_name="CoherentPluggableBlock"
):
    """Base class for inactive CoherentPluggableBlock product blocks."""

    optical_port_role: Literal[OpticalPortRole.COHERENT_PLUGGABLE] = OpticalPortRole.COHERENT_PLUGGABLE
    host_node: OpticalPacketNodeBlockInactive | None = None
    optical_coherent_pluggable_firmware_version: str | None = None

    @computed_field
    @property
    def optical_coherent_pluggable_part_number(self) -> str:
        """From fixed_inputs."""
        sub = SubscriptionModel.from_subscription(self.owner_subscription_id)
        return sub.optical_coherent_pluggable_part_number  # ty: ignore[unresolved-attribute] # We can't cast to the Product Type since that would cause a circular import


class OpticalCoherentPluggableBlockProvisioning(
    OpticalCoherentPluggableBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Base class for provisioning CoherentPluggableBlock product blocks."""

    optical_port_role: Literal[OpticalPortRole.COHERENT_PLUGGABLE] = OpticalPortRole.COHERENT_PLUGGABLE
    host_node: OpticalPacketNodeBlockProvisioning
    optical_coherent_pluggable_firmware_version: str


class OpticalCoherentPluggableBlock(
    OpticalCoherentPluggableBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Base class for active CoherentPluggableBlock product blocks."""

    optical_port_role: Literal[OpticalPortRole.COHERENT_PLUGGABLE] = OpticalPortRole.COHERENT_PLUGGABLE
    host_node: OpticalPacketNodeBlock
    optical_coherent_pluggable_firmware_version: str
