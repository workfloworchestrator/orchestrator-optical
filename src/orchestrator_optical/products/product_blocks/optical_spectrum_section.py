"""Module for OpticalSpectrumSectionBlock product blocks."""

from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_port import (
    OlsAddDropPortBlock,
    OlsAddDropPortBlockInactive,
    OlsAddDropPortBlockProvisioning,
    OlsLinePortBlock,
    OlsLinePortBlockInactive,
    OlsLinePortBlockProvisioning,
)

AddDropPorts = Annotated[list[SI], Len(min_length=2, max_length=2), "List of add/drop ports."]

ExpressPorts = Annotated[list[SI], Len(min_length=0, max_length=64), "List of ports representing the express path."]

# --- Inactive ---


class OpticalSpectrumSectionBlockInactive(ProductBlockModel, product_block_name="OpticalSpectrumSection"):
    """Inactive state of an OpticalSpectrumSectionBlock product block."""

    add_drop_ports: AddDropPorts[OlsAddDropPortBlockInactive] = Field(default_factory=list)
    express_ports: ExpressPorts[OlsLinePortBlockInactive] = Field(default_factory=list)


# --- Provisioning ---


class OpticalSpectrumSectionBlockProvisioning(
    OpticalSpectrumSectionBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Provisioning state of an OpticalSpectrumSectionBlock product block."""

    add_drop_ports: AddDropPorts[OlsAddDropPortBlockProvisioning]
    express_ports: ExpressPorts[OlsLinePortBlockProvisioning]


# --- Active ---


class OpticalSpectrumSectionBlock(OpticalSpectrumSectionBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an OpticalSpectrumSectionBlock product block."""

    add_drop_ports: AddDropPorts[OlsAddDropPortBlock]
    express_ports: ExpressPorts[OlsLinePortBlock]
