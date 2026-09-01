"""Module for Optical Port product blocks."""

from typing import Literal

from pydantic import computed_field

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.optical_packet_node import (
    OpticalModulePacketNodeBlock,
    OpticalModulePacketNodeBlockInactive,
    OpticalModulePacketNodeBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port._abstracts import (
    _AbstractOpticalPortBlock,
    _AbstractOpticalPortBlockInactive,
    _AbstractOpticalPortBlockProvisioning,
    OpticalPortRole,
)


class OpticalCoherentPluggableBlockInactive(
    _AbstractOpticalPortBlockInactive, product_block_name="CoherentPluggableBlock"
):
    """Base class for inactive CoherentPluggableBlock product blocks."""

    optical_port_role: Literal[OpticalPortRole.COHERENT_PLUGGABLE] = OpticalPortRole.COHERENT_PLUGGABLE
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_coherent_pluggable_firmware_version: str | None = None

    optical_port_host_node: OpticalModulePacketNodeBlockInactive

    @computed_field
    @property
    def optical_coherent_pluggable_part_number(self) -> str:
        """From fixed_inputs."""
        sub = SubscriptionModel.from_subscription(self.owner_subscription_id)
        # pyrefly: ignore [missing-attribute]  # noqa: ERA001
        return sub.optical_coherent_pluggable_part_number  # ty: ignore[unresolved-attribute] # We can't cast to the Product Type since that would cause a circular import


class OpticalCoherentPluggableBlockProvisioning(
    OpticalCoherentPluggableBlockInactive,
    _AbstractOpticalPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base class for provisioning CoherentPluggableBlock product blocks."""

    optical_port_role: Literal[OpticalPortRole.COHERENT_PLUGGABLE] = OpticalPortRole.COHERENT_PLUGGABLE
    optical_port_name: str
    optical_port_description: str | None
    optical_coherent_pluggable_firmware_version: str

    optical_port_host_node: OpticalModulePacketNodeBlockProvisioning


class OpticalCoherentPluggableBlock(
    OpticalCoherentPluggableBlockProvisioning, _AbstractOpticalPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Base class for active CoherentPluggableBlock product blocks."""

    optical_port_role: Literal[OpticalPortRole.COHERENT_PLUGGABLE] = OpticalPortRole.COHERENT_PLUGGABLE
    optical_port_name: str
    optical_port_description: str | None
    optical_coherent_pluggable_firmware_version: str

    optical_port_host_node: OpticalModulePacketNodeBlock
