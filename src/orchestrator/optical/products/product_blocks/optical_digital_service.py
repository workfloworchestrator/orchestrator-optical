"""Module for Optical Digital Service product blocks."""

from typing import Annotated

from annotated_types import Len
from pydantic import Field

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SI, SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_port.unions import (
    OpticalDigitalServiceClientPortBlock,
    OpticalDigitalServiceClientPortBlockInactive,
    OpticalDigitalServiceClientPortBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_transport_channel import (
    OpticalTransportChannelBlock,
    OpticalTransportChannelBlockInactive,
    OpticalTransportChannelBlockProvisioning,
)

OpticalClientPortList = Annotated[list[SI], Len(min_length=2, max_length=2)]
OpticalTransportChannelList = Annotated[
    list[SI],
    Len(min_length=1, max_length=2),
    "Two channels means reverse multiplexing: two transport channels for one client service.",
]


class OpticalDigitalServiceBlockInactive(ProductBlockModel, product_block_name="OpticalDigitalServiceBlock"):
    """Inactive state of an Optical Digital Service product block."""

    optical_digital_service_name: str | None = None
    optical_digital_service_client_ports: OpticalClientPortList[OpticalDigitalServiceClientPortBlockInactive] = Field(
        default_factory=list
    )
    optical_digital_service_transport_channels: OpticalTransportChannelList[OpticalTransportChannelBlockInactive] = (
        Field(default_factory=list)
    )


class OpticalDigitalServiceBlockProvisioning(
    OpticalDigitalServiceBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Provisioning state of an Optical Digital Service product block."""

    optical_digital_service_name: str
    optical_digital_service_client_ports: OpticalClientPortList[OpticalDigitalServiceClientPortBlockProvisioning]
    optical_digital_service_transport_channels: OpticalTransportChannelList[OpticalTransportChannelBlockProvisioning]


class OpticalDigitalServiceBlock(OpticalDigitalServiceBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an Optical Digital Service product block."""

    optical_digital_service_name: str
    optical_digital_service_client_ports: OpticalClientPortList[OpticalDigitalServiceClientPortBlock]
    optical_digital_service_transport_channels: OpticalTransportChannelList[OpticalTransportChannelBlock]
