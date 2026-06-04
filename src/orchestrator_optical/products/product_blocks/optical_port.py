"""Module for Optical Port product blocks."""

from enum import StrEnum
from typing import Annotated, Literal

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Field

from orchestrator_optical.products.product_blocks.optical_node import (
    OpticalNodeBlockUnion,
    OpticalNodeBlockUnionInactive,
    OpticalNodeBlockUnionProvisioning,
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


class AbstractPortBlockInactive(ProductBlockModel):
    """missing docstring."""

    role: PortRole
    port_name: str | None = None
    port_description: str | None = None
    host_node: OpticalNodeBlockUnionInactive


class AbstractPassbandPortBlockInactive(AbstractPortBlockInactive):
    passbands: ListOfPassbands = Field(default_factory=list)


class TransponderClientPortBlockInactive(AbstractPortBlockInactive, product_block_name="TransponderClientPort"):
    role: Literal[PortRole.TRANSPONDER_CLIENT] = PortRole.TRANSPONDER_CLIENT
    host_node: OpticalNodeBlockUnionInactive


class TransponderLinePortBlockInactive(AbstractPortBlockInactive, product_block_name="TransponderLinePort"):
    role: Literal[PortRole.TRANSPONDER_LINE] = PortRole.TRANSPONDER_LINE
    host_node: OpticalNodeBlockUnionInactive


class OlsAddDropPortBlockInactive(AbstractPassbandPortBlockInactive, product_block_name="OlsAddDropPort"):
    role: Literal[PortRole.OLS_ADD_DROP] = PortRole.OLS_ADD_DROP
    host_node: OpticalNodeBlockUnionInactive


class OlsLinePortBlockInactive(AbstractPassbandPortBlockInactive, product_block_name="OlsLinePort"):
    role: Literal[PortRole.OLS_LINE] = PortRole.OLS_LINE
    host_node: OpticalNodeBlockUnionInactive


# --- Provisioning ---


class AbstractPortBlockProvisioning(AbstractPortBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    port_name: str
    host_node: OpticalNodeBlockUnionProvisioning


class AbstractPassbandPortBlockProvisioning(
    AbstractPassbandPortBlockInactive, AbstractPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    passbands: ListOfPassbands


class TransponderClientPortBlockProvisioning(
    TransponderClientPortBlockInactive, AbstractPortBlockProvisioning, lifecycle=SubscriptionLifecycle.PROVISIONING
):
    host_node: OpticalNodeBlockUnionProvisioning


class TransponderLinePortBlockProvisioning(
    TransponderLinePortBlockInactive, AbstractPortBlockProvisioning, lifecycle=SubscriptionLifecycle.PROVISIONING
):
    host_node: OpticalNodeBlockUnionProvisioning


class OlsAddDropPortBlockProvisioning(
    OlsAddDropPortBlockInactive, AbstractPassbandPortBlockProvisioning, lifecycle=SubscriptionLifecycle.PROVISIONING
):
    host_node: OpticalNodeBlockUnionProvisioning


class OlsLinePortBlockProvisioning(
    OlsLinePortBlockInactive, AbstractPassbandPortBlockProvisioning, lifecycle=SubscriptionLifecycle.PROVISIONING
):
    host_node: OpticalNodeBlockUnionProvisioning


# --- Active ---


class AbstractPortBlock(AbstractPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    port_description: str
    host_node: OpticalNodeBlockUnion


class AbstractPassbandPortBlock(
    AbstractPassbandPortBlockProvisioning, AbstractPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    host_node: OpticalNodeBlockUnion


class TransponderClientPortBlock(TransponderClientPortBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    host_node: OpticalNodeBlockUnion


class TransponderLinePortBlock(TransponderLinePortBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    host_node: OpticalNodeBlockUnion


class OlsAddDropPortBlock(OlsAddDropPortBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    host_node: OpticalNodeBlockUnion


class OlsLinePortBlock(OlsLinePortBlockProvisioning, lifecycle=SubscriptionLifecycle.ACTIVE):
    host_node: OpticalNodeBlockUnion


# --- Union Types ---
OpticalPortBlocksUnion = Annotated[
    OlsAddDropPortBlock | OlsLinePortBlock | TransponderClientPortBlock | TransponderLinePortBlock,
    Field(discriminator="role"),
]
