"""Module for Optical Port product blocks.

There is a product block for each kind of Optical Port Role, in each subscription lifecycle state.
"""

from typing import Annotated, Literal

from annotated_types import Len
from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle
from pydantic import Field
from pydantic_forms.types import strEnum

from orchestrator_optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)
from orchestrator_optical.utils.custom_types.frequencies import Passband

OpticalPassbandList = Annotated[list[Passband], Len(min_length=0, max_length=128), "List of used passbands (MHz, MHz)."]


class OpticalPortRole(strEnum):
    """The Role of the Optical Port."""

    OLS_ADD_DROP = "Optical Line System Add/Drop"
    OLS_LINE = "Optical Line System Line"
    TRANSPONDER_CLIENT = "Transponder Client"
    TRANSPONDER_LINE = "Transponder Line"
    COHERENT_PLUGGABLE = "Coherent Pluggable"


class AbstractOpticalPortBlockInactive(ProductBlockModel, product_block_name="AbstractOpticalPortBlock"):
    """Abstract implementation of an Optical Port Product Block that is inactive."""

    optical_port_role: OpticalPortRole | None = None
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_port_host_node: AbstractOpticalNodeBlockInactive


class AbstractOpticalPortBlockProvisioning(
    AbstractOpticalPortBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract implementation of an Optical Port Product Block that is provisioning."""

    optical_port_role: OpticalPortRole
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: AbstractOpticalNodeBlockProvisioning


class AbstractOpticalPortBlock(AbstractOpticalPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract implementation of an Optical Port Product Block that is active."""

    optical_port_role: OpticalPortRole
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: AbstractOpticalNodeBlock


class AbstractOpticalOlsPortBlockInactive(
    AbstractOpticalPortBlockInactive, product_block_name="AbstractOpticalOlsPortBlock"
):
    """Abstract implementation of an Optical Port Block with passbands that is inactive."""

    optical_passbands: OpticalPassbandList = Field(default_factory=list)
    optical_host_node: AbstractOpticalNodeBlockInactive


class AbstractOpticalOlsPortBlockProvisioning(
    AbstractOpticalOlsPortBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract implementation of an Optcial Port Block with passbands that is provisioning."""

    optical_passbands: OpticalPassbandList
    optical_host_node: AbstractOpticalNodeBlockProvisioning


class AbstractOpticalOlsPortBlock(AbstractOpticalOlsPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract implementation of an Optical Port Block with passbands that is active."""

    optical_passbands: OpticalPassbandList
    optical_host_node: AbstractOpticalNodeBlock


class OlsAddDropPortBlockInactive(AbstractOpticalOlsPortBlockInactive, product_block_name="OlsAddDropPortBlock"):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_ADD_DROP] = OpticalPortRole.OLS_ADD_DROP


class OlsAddDropPortBlockProvisioning(
    OlsAddDropPortBlockInactive, AbstractOpticalOlsPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_ADD_DROP] = OpticalPortRole.OLS_ADD_DROP


class OlsAddDropPortBlock(
    OlsAddDropPortBlockProvisioning, AbstractOpticalOlsPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_ADD_DROP] = OpticalPortRole.OLS_ADD_DROP


class OlsLinePortBlockInactive(AbstractOpticalOlsPortBlockInactive, product_block_name="OlsLinePortBlock"):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_LINE] = OpticalPortRole.OLS_LINE


class OlsLinePortBlockProvisioning(
    OlsLinePortBlockInactive, AbstractOpticalOlsPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_LINE] = OpticalPortRole.OLS_LINE


class OlsLinePortBlock(
    OlsLinePortBlockProvisioning, AbstractOpticalOlsPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """OLS Add Drop Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.OLS_LINE] = OpticalPortRole.OLS_LINE


class OpticalTransponderClientPortBlockInactive(
    AbstractOpticalPortBlockInactive, product_block_name="OpticalTransponderClientPortBlock"
):
    """Optical Transponder Client Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_CLIENT] = OpticalPortRole.TRANSPONDER_CLIENT


class OpticalTransponderClientPortBlockProvisioning(
    OpticalTransponderClientPortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Optical Transponder Client Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_CLIENT] = OpticalPortRole.TRANSPONDER_CLIENT


class OpticalTransponderClientPortBlock(
    OpticalTransponderClientPortBlockProvisioning, AbstractOpticalPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Optical Transponder Client Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_CLIENT] = OpticalPortRole.TRANSPONDER_CLIENT


class OpticalTransponderLinePortBlockInactive(
    AbstractOpticalPortBlockInactive, product_block_name="OpticalTransponderLinePortBlock"
):
    """Optical Transponder Line Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_LINE] = OpticalPortRole.TRANSPONDER_LINE


class OpticalTransponderLinePortBlockProvisioning(
    OpticalTransponderLinePortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Optical Transponder Line Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_LINE] = OpticalPortRole.TRANSPONDER_LINE


class OpticalTransponderLinePortBlock(
    OpticalTransponderLinePortBlockProvisioning, AbstractOpticalPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Optical Transponder Line Port Product Block that is inactive."""

    optical_port_role: Literal[OpticalPortRole.TRANSPONDER_LINE] = OpticalPortRole.TRANSPONDER_LINE
