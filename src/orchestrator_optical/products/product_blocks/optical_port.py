"""Module for Optical Port product blocks."""

from enum import StrEnum
from typing import Annotated, Literal

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_node import (
    OpticalNodeBlockUnionInactive,
    OpticalNodeBlockUnionProvisioning,
    OpticalNodeBlockUnion,
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
    host_node: OpticalNodeBlockUnionInactive


class OlsAddDropPortBlockInactive(_PortInactive, product_block_name="OlsAddDropPort"):
    role: Literal[PortRole.OLS_ADD_DROP] = PortRole.OLS_ADD_DROP
    passbands: ListOfPassbands = Field(default_factory=list)
    host_node: OpticalNodeBlockUnionInactive


class OlsLinePortBlockInactive(_PortInactive, product_block_name="OlsLinePort"):
    role: Literal[PortRole.OLS_LINE] = PortRole.OLS_LINE
    passbands: ListOfPassbands = Field(default_factory=list)
    host_node: OpticalNodeBlockUnionInactive


class TransponderClientPortBlockInactive(_PortInactive, product_block_name="TransponderClientPort"):
    role: Literal[PortRole.TRANSPONDER_CLIENT] = PortRole.TRANSPONDER_CLIENT
    host_node: OpticalNodeBlockUnionInactive


class TransponderLinePortBlockInactive(_PortInactive, product_block_name="TransponderLinePort"):
    role: Literal[PortRole.TRANSPONDER_LINE] = PortRole.TRANSPONDER_LINE
    host_node: OpticalNodeBlockUnionInactive


# --- Provisioning ---


class OlsAddDropPortBlockProvisioning(OlsAddDropPortBlockInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    port_name: str
    host_node: OpticalNodeBlockUnionProvisioning


class OlsLinePortBlockProvisioning(OlsLinePortBlockInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    port_name: str
    host_node: OpticalNodeBlockUnionProvisioning


class TransponderClientPortBlockProvisioning(TransponderClientPortBlockInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    port_name: str
    host_node: OpticalNodeBlockUnionProvisioning


class TransponderLinePortBlockProvisioning(TransponderLinePortBlockInactive, lifecycle=SubscriptionLifecycle.PROVISIONING):
    port_name: str
    host_node: OpticalNodeBlockUnionProvisioning


# --- Active ---


class OlsAddDropPortBlock(OlsAddDropPortBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    port_description: str
    host_node: OpticalNodeBlockUnion


class OlsLinePortBlock(OlsLinePortBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    port_description: str
    host_node: OpticalNodeBlockUnion


class TransponderClientPortBlock(TransponderClientPortBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    port_description: str
    host_node: OpticalNodeBlockUnion


class TransponderLinePortBlock(TransponderLinePortBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    port_description: str
    host_node: OpticalNodeBlockUnion


# --- Union Types ---
OpticalPortBlocksUnion = Annotated[
    OlsAddDropPortBlock | OlsLinePortBlock | TransponderClientPortBlock | TransponderLinePortBlock, Field(discriminator="role")
]
