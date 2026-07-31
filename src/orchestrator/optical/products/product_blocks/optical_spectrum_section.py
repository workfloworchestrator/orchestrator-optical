"""Module for OpticalSpectrumSectionBlock product blocks."""

from typing import Annotated

from annotated_types import Len
from pydantic import Field

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SI, SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_port import (
    OlsAddDropPortBlock,
    OlsAddDropPortBlockInactive,
    OlsAddDropPortBlockProvisioning,
    OlsLinePortBlock,
    OlsLinePortBlockInactive,
    OlsLinePortBlockProvisioning,
)

AddDropPorts = Annotated[list[SI], Len(min_length=2, max_length=2), "List of add/drop ports."]
ExpressPortList = Annotated[list[SI], Len(min_length=0, max_length=64), "List of ports representing the express path."]


class OpticalSpectrumSectionBlockInactive(ProductBlockModel, product_block_name="OpticalSpectrumSectionBlock"):
    """Inactive state of an OpticalSpectrumSectionBlock product block."""

    optical_pipe_add_drop_ports: AddDropPorts[OlsAddDropPortBlockInactive] = Field(default_factory=list)
    optical_express_ports: ExpressPortList[OlsLinePortBlockInactive] = Field(default_factory=list)


class OpticalSpectrumSectionBlockProvisioning(
    OpticalSpectrumSectionBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Provisioning state of an OpticalSpectrumSectionBlock product block."""

    optical_pipe_add_drop_ports: AddDropPorts[OlsAddDropPortBlockProvisioning]
    optical_pipe_express_ports: ExpressPortList[OlsLinePortBlockProvisioning]


class OpticalSpectrumSectionBlock(OpticalSpectrumSectionBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an OpticalSpectrumSectionBlock product block."""

    optical_pipe_add_drop_ports: AddDropPorts[OlsAddDropPortBlock]
    optical_pipe_express_ports: ExpressPortList[OlsLinePortBlock]
