"""Abstract implementations of Optical Port Product Blocks."""

from typing import Annotated

from annotated_types import Len
from pydantic import Field
from pydantic_forms.types import strEnum

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.unions import (
    AnyOpticalNodeBlockInactiveUnion,
    AnyOpticalNodeBlockProvisioningUnion,
    AnyOpticalNodeBlockUnion,
    OlsBlockInactiveUnion,
    OlsBlockProvisioningUnion,
    OlsBlockUnion,
)
from orchestrator.optical.utils.custom_types.frequencies import Passband

OpticalPassbandList = Annotated[list[Passband], Len(min_length=0, max_length=128), "List of used passbands (MHz, MHz)."]


class OpticalPortRole(strEnum):
    """The Role of the Optical Port."""

    OLS_ADD_DROP = "Optical Line System Add/Drop"
    OLS_LINE = "Optical Line System Line"
    TRANSPONDER_CLIENT = "Transponder Client"
    TRANSPONDER_LINE = "Transponder Line"
    COHERENT_PLUGGABLE = "Coherent Pluggable"


class AbstractOpticalPortBlockInactive(ProductBlockModel):
    """Abstract implementation of an Optical Port Product Block that is inactive."""

    optical_port_role: OpticalPortRole | None = None
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_port_host_node: AnyOpticalNodeBlockInactiveUnion


class AbstractOpticalPortBlockProvisioning(
    AbstractOpticalPortBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract implementation of an Optical Port Product Block that is provisioning."""

    optical_port_role: OpticalPortRole
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: AnyOpticalNodeBlockProvisioningUnion


class AbstractOpticalPortBlock(AbstractOpticalPortBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract implementation of an Optical Port Product Block that is active."""

    optical_port_role: OpticalPortRole
    optical_port_name: str
    optical_port_description: str | None
    optical_port_host_node: AnyOpticalNodeBlockUnion


class AbstractOpticalOlsPortBlockInactive(AbstractOpticalPortBlockInactive):
    """Abstract implementation of an Optical Port Block with passbands that is inactive."""

    optical_port_role: OpticalPortRole | None = None
    optical_port_name: str | None = None
    optical_port_description: str | None = None
    optical_passbands: OpticalPassbandList = Field(default_factory=list)
    optical_port_host_node: OlsBlockInactiveUnion


class AbstractOpticalOlsPortBlockProvisioning(
    AbstractOpticalOlsPortBlockInactive,
    AbstractOpticalPortBlockProvisioning,
    lifecycle=[SubscriptionLifecycle.PROVISIONING],
):
    """Abstract implementation of an Optcial Port Block with passbands that is provisioning."""

    optical_port_role: OpticalPortRole
    optical_port_name: str
    optical_port_description: str | None
    optical_passbands: OpticalPassbandList
    optical_port_host_node: OlsBlockProvisioningUnion


class AbstractOpticalOlsPortBlock(
    AbstractOpticalOlsPortBlockProvisioning, AbstractOpticalPortBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Abstract implementation of an Optical Port Block with passbands that is active."""

    optical_port_role: OpticalPortRole
    optical_port_name: str
    optical_port_description: str | None
    optical_passbands: OpticalPassbandList
    optical_port_host_node: OlsBlockUnion
