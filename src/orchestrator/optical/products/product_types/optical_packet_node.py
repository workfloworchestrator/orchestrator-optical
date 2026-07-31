"""Abstract Product Types of an Optical Packet Node."""

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_packet_node import (
    AbstractOpticalPacketNodeBlock,
    AbstractOpticalPacketNodeBlockInactive,
    AbstractOpticalPacketNodeBlockProvisioning,
)


class AbstractOpticalPacketNodeInactive(SubscriptionModel, is_base=True):
    """Abstract model of an Optical Packet Node that is inactive."""

    optical_packet_node: AbstractOpticalPacketNodeBlockInactive


class AbstractOpticalPacketNodeProvisioning(
    AbstractOpticalPacketNodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract model of an Optical Packet Node that is provisioning."""

    optical_packet_node: AbstractOpticalPacketNodeBlockProvisioning


class AbstractOpticalPacketNode(AbstractOpticalPacketNodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract model of an Optical Packet Node."""

    optical_packet_node: AbstractOpticalPacketNodeBlock
