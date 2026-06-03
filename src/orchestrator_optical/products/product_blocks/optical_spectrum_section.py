"""Module for OpticalSpectrumSection product blocks."""
from typing import Annotated

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SI, SubscriptionLifecycle

from orchestrator_optical.products.product_blocks.optical_port import (
    OlsAddDropPort,
    OlsAddDropPortInactive,
    OlsAddDropPortProvisioning,
    OlsLinePort,
    OlsLinePortInactive,
    OlsLinePortProvisioning,
)

AddDropPorts = Annotated[list[SI], Len(min_length=2, max_length=2), "List of add/drop ports."]

ExpressPorts = Annotated[list[SI], Len(min_length=0, max_length=64), "List of ports representing the express path."]

# --- Inactive ---


class OpticalSpectrumSectionInactive(
    ProductBlockModel, product_block_name="OpticalSpectrumSection"
):
    """Inactive state of an OpticalSpectrumSection product block."""

    add_drop_ports: AddDropPorts[OlsAddDropPortInactive]
    express_ports: ExpressPorts[OlsLinePortInactive]


# --- Provisioning ---


class OpticalSpectrumSectionProvisioning(
    OpticalSpectrumSectionInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Provisioning state of an OpticalSpectrumSection product block."""

    add_drop_ports: AddDropPorts[OlsAddDropPortProvisioning]
    express_ports: ExpressPorts[OlsLinePortProvisioning]


# --- Active ---


class OpticalSpectrumSection(OpticalSpectrumSectionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Active state of an OpticalSpectrumSection product block."""

    add_drop_ports: AddDropPorts[OlsAddDropPort]
    express_ports: ExpressPorts[OlsLinePort]


