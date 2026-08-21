"""Abstract Product Types of an Optical Packet Node."""

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_packet_node import (
    OpticalModulePacketNode,
    OpticalModulePacketNodeInactive,
    OpticalModulePacketNodeProvisioning,
)


class OpticalModulePacketNodeSubscriptionInactive(SubscriptionModel, is_base=True):
    """Abstract model of an Optical Packet Node that is inactive."""

    optical_packet_node: OpticalModulePacketNodeInactive


class OpticalModulePacketNodeSubscriptionProvisioning(
    OpticalModulePacketNodeSubscriptionInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract model of an Optical Packet Node that is provisioning."""

    optical_packet_node: OpticalModulePacketNodeProvisioning


class OpticalModulePacketNodeSubscription(OpticalModulePacketNodeSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract model of an Optical Packet Node."""

    optical_packet_node: OpticalModulePacketNode
