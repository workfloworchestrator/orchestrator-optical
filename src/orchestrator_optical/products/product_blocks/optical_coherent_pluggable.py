"""Module for Optical Port product blocks."""

from typing import Literal

from orchestrator.domain import SubscriptionModel
from pydantic import computed_field

from orchestrator_optical.products.product_blocks.optical_packet_node import (
    OpticalPacketNodeBlock,
    OpticalPacketNodeInactive,
    OpticalPacketNodeProvisioning,
)
from orchestrator_optical.products.product_blocks.optical_port import (
    OpticalPortBlock,
    OpticalPortProvisioning,
    PortRole,
    _PortInactive,
)


class CoherentPluggableInactive(_PortInactive):
    """Base class for inactive CoherentPluggable product blocks."""

    role: Literal[PortRole.COHERENT_PLUGGABLE] = PortRole.COHERENT_PLUGGABLE
    fw_version: str | None = None
    host_node: OpticalPacketNodeInactive | None = None

    @computed_field
    @property
    def vendor_and_part_no(self) -> str:
        """From fixed_inputs."""
        sub = SubscriptionModel.from_subscription(self.owner_subscription_id)
        return sub.vendor_and_part_no


class CoherentPluggableProvisioning(
    CoherentPluggableInactive, OpticalPortProvisioning
):
    """Base class for provisioning CoherentPluggable product blocks."""

    fw_version: str
    host_node: OpticalPacketNodeProvisioning


class CoherentPluggable(CoherentPluggableProvisioning, OpticalPortBlock):
    """Base class for active CoherentPluggable product blocks."""

    host_node: OpticalPacketNodeBlock
