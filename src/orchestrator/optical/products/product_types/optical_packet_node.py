"""Abstract Product Types of an Optical Packet Node."""

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.optical_packet_node import (
    OpticalModulePacketNodeBlock,
    OpticalModulePacketNodeBlockInactive,
    OpticalModulePacketNodeBlockProvisioning,
)


class OpticalModulePacketNodeSubscriptionInactive(SubscriptionModel, is_base=True):
    """Abstract model of an Optical Packet Node that is inactive."""

    optical_packet_node: OpticalModulePacketNodeBlockInactive


class OpticalModulePacketNodeSubscriptionProvisioning(
    OpticalModulePacketNodeSubscriptionInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract model of an Optical Packet Node that is provisioning."""

    optical_packet_node: OpticalModulePacketNodeBlockProvisioning


class OpticalModulePacketNodeSubscription(
    OpticalModulePacketNodeSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Abstract model of an Optical Packet Node."""

    optical_packet_node: OpticalModulePacketNodeBlock
