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
from orchestrator_optical.products.product_blocks.optical_port import (
    AbstractPortBlock,
    AbstractPortBlockInactive,
    AbstractPortBlockProvisioning,
    PortRole,
)


class CoherentPluggableBlockInactive(AbstractPortBlockInactive, product_block_name="CoherentPluggable"):
    """Base class for inactive CoherentPluggableBlock product blocks."""

    role: Literal[PortRole.COHERENT_PLUGGABLE] = PortRole.COHERENT_PLUGGABLE
    fw_version: str | None = None
    host_node: OpticalPacketNodeBlockInactive | None = None

    @computed_field
    @property
    def vendor_and_part_no(self) -> str:
        """From fixed_inputs."""
        sub = SubscriptionModel.from_subscription(self.owner_subscription_id)
        return sub.vendor_and_part_no


class CoherentPluggableBlockProvisioning(
    CoherentPluggableBlockInactive, AbstractPortBlockProvisioning, lifecycle=SubscriptionLifecycle.PROVISIONING
):
    """Base class for provisioning CoherentPluggableBlock product blocks."""

    fw_version: str
    host_node: OpticalPacketNodeBlockProvisioning


class CoherentPluggableBlock(
    CoherentPluggableBlockProvisioning, AbstractPortBlock, lifecycle=SubscriptionLifecycle.ACTIVE
):
    """Base class for active CoherentPluggableBlock product blocks."""

    host_node: OpticalPacketNodeBlock
