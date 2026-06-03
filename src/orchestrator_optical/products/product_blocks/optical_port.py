"""Module for Optical Port product blocks."""

from enum import StrEnum
from typing import Annotated, Literal

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_node import (
    OpticalNodeInactiveUnion,
    OpticalNodeProvisioningUnion,
    OpticalNodeUnion,
)
from orchestrator_optical.utils.custom_types.frequencies import Passband

# --- Types & Enums ---

ListOfPassbands = Annotated[list[Passband], Len(min_length=0, max_length=128), "List of used passbands (MHz, MHz)."]


class PortRole(StrEnum):
    """missing docstring."""

    OLS_ADD_DROP = "Optical Line System Add/Drop"
    OLS_LINE = "Optical Line System Line"
    TRANSPONDER_CLIENT = "Transponder Client"
    TRANSPONDER_LINE = "Transponder Line"
    COHERENT_PLUGGABLE = "Coherent Pluggable"


# --- Inactive ---


class _PortInactive(ProductBlockModel):
    """missing docstring."""

    role: PortRole
    port_name: str | None = None
    port_description: str | None = None
    host_node: OpticalNodeInactiveUnion


class OlsAddDropPortInactive(_PortInactive, product_block_name="OlsAddDropPort"):
    role: Literal[PortRole.OLS_ADD_DROP] = PortRole.OLS_ADD_DROP
    passbands: ListOfPassbands = Field(default_factory=list)
    host_node: OpticalNodeInactiveUnion


class OlsLinePortInactive(_PortInactive, product_block_name="OlsLinePort"):
    role: Literal[PortRole.OLS_LINE] = PortRole.OLS_LINE
    passbands: ListOfPassbands = Field(default_factory=list)
    host_node: OpticalNodeInactiveUnion


class TransponderClientPortInactive(_PortInactive, product_block_name="TransponderClientPort"):
    role: Literal[PortRole.TRANSPONDER_CLIENT] = PortRole.TRANSPONDER_CLIENT
    host_node: OpticalNodeInactiveUnion


class TransponderLinePortInactive(_PortInactive, product_block_name="TransponderLinePort"):
    role: Literal[PortRole.TRANSPONDER_LINE] = PortRole.TRANSPONDER_LINE
    host_node: OpticalNodeInactiveUnion


# --- Provisioning ---


class OlsAddDropPortProvisioning(OlsAddDropPortInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    port_name: str
    host_node: OpticalNodeProvisioningUnion


class OlsLinePortProvisioning(OlsLinePortInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    port_name: str
    host_node: OpticalNodeProvisioningUnion


class TransponderClientPortProvisioning(TransponderClientPortInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    port_name: str
    host_node: OpticalNodeProvisioningUnion


class TransponderLinePortProvisioning(TransponderLinePortInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    port_name: str
    host_node: OpticalNodeProvisioningUnion


# --- Active ---


class OlsAddDropPort(OlsAddDropPortProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    port_description: str
    host_node: OpticalNodeUnion


class OlsLinePort(OlsLinePortProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    port_description: str
    host_node: OpticalNodeUnion


class TransponderClientPort(TransponderClientPortProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    port_description: str
    host_node: OpticalNodeUnion


class TransponderLinePort(TransponderLinePortProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    port_description: str
    host_node: OpticalNodeUnion


# --- Union Types ---
OpticalPortUnion = Annotated[
    OlsAddDropPort | OlsLinePort | TransponderClientPort | TransponderLinePort, Field(discriminator="role")
]
