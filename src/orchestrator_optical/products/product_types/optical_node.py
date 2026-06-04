"""Models for the subscriptions of optical nodes."""

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle


class AbstractOpticalNodeInactive(SubscriptionModel):
    """Abstract base model for an optical node subscription in the inactive state."""

    optical_node: AbstractOpticalNodeBlockInactive


class AbstractOpticalNodeProvisioning(AbstractOpticalNodeInactive):
    """Abstract base model for an optical node subscription in the provisioning state."""

    optical_node: AbstractOpticalNodeBlockProvisioning


class AbstractOpticalNode(AbstractOpticalNodeProvisioning):
    """Abstract base model for an optical node subscription in the active state."""

    optical_node: AbstractOpticalNodeBlock


class OpticalNodeNokiaGrooveG30Inactive(AbstractOpticalNodeInactive, is_base=True):
    """A Nokia Groove G30 Optical Node that is inactive."""

    optical_node: OpticalNodeNokiaGrooveG30BlockInactive


class OpticalNodeNokiaGrooveG30Provisioning(
    AbstractOpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Nokia Groove G30 Optical Node that is provisioning."""

    optical_node: OpticalNodeNokiaGrooveG30BlockProvisioning


class OpticalNodeNokiaGrooveG30(AbstractOpticalNode, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """A Nokia Groove G30 Optical Node that is active."""

    optical_node: OpticalNodeNokiaGrooveG30Block


class OpticalNodeNokiaGxG42Inactive(AbstractOpticalNodeInactive, is_base=True):
    """A Nokia GX G42 Optical Node that is inactive."""

    optical_node: OpticalNodeNokiaGxG42BlockInactive


class OpticalNodeNokiaGxG42Provisioning(
    AbstractOpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Nokia GX G42 Optical Node that is provisioning."""

    optical_node: OpticalNodeNokiaGxG42BlockProvisioning


class OpticalNodeNokiaGxG42(AbstractOpticalNode, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """A Nokia GX G42 Optical Node that is active."""

    optical_node: OpticalNodeNokiaGxG42Block


class OpticalNodeNokiaFlexIlsInactive(AbstractOpticalNodeInactive, is_base=True):
    """A Nokia FlexILS Optical Node that is inactive."""

    optical_node: OpticalNodeNokiaFlexIlsBlockInactive


class OpticalNodeNokiaFlexIlsProvisioning(
    AbstractOpticalNodeProvisioning, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """A Nokia FlexILS Optical Node that is provisioning."""

    optical_node: OpticalNodeNokiaFlexIlsBlockProvisioning


class OpticalNodeNokiaFlexIls(AbstractOpticalNode, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """A Nokia FlexILS Optical Node that is active."""

    optical_node: OpticalNodeNokiaFlexIlsBlock
