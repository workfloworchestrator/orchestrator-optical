"""Module for Optical Port product blocks."""

from pydantic_forms.types import strEnum

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.optical_packet_node import (
    OpticalModulePacketNodeBlock,
    OpticalModulePacketNodeBlockInactive,
    OpticalModulePacketNodeBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalPortBlock,
    AbstractOpticalPortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    OpticalPortRole,
)


class OpticalCoherentPluggablePartNumber(strEnum):
    """Enumerate supported optical device vendor and part numbers."""

    CISCO_QDD_400G_ZRP_S = "CISCO QDD-400G-ZRP-S"
    CISCO_DP04QSDD_HK9 = "CISCO DP04QSDD-HK9"


class OpticalCoherentPluggableBlockInactive(
    AbstractOpticalPortBlockInactive, product_block_name="CoherentPluggableBlock"
):
    """Base class for inactive CoherentPluggableBlock product blocks."""

    optical_port_role: OpticalPortRole = OpticalPortRole.COHERENT_PLUGGABLE
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_coherent_pluggable_firmware_version: str | None = None
    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber | None = None

    optical_port_host_node: OpticalModulePacketNodeBlockInactive


class OpticalCoherentPluggableBlockProvisioning(
    OpticalCoherentPluggableBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Base class for provisioning CoherentPluggableBlock product blocks."""

    optical_port_role: OpticalPortRole = OpticalPortRole.COHERENT_PLUGGABLE
    optical_port_name: str
    optical_port_description: str | None
    optical_coherent_pluggable_firmware_version: str
    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber

    optical_port_host_node: OpticalModulePacketNodeBlockProvisioning


class OpticalCoherentPluggableBlock(
    OpticalCoherentPluggableBlockProvisioning, AbstractOpticalPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Base class for active CoherentPluggableBlock product blocks."""

    optical_port_role: OpticalPortRole = OpticalPortRole.COHERENT_PLUGGABLE
    optical_port_name: str
    optical_port_description: str | None
    optical_coherent_pluggable_firmware_version: str
    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber

    optical_port_host_node: OpticalModulePacketNodeBlock
