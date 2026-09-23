"""Shared consumer-style model chains used by the composition tests.

Each chain composes one shipped optical block under a consumer-owned block and
subscription model, mirroring how a consumer would has-a the shipped blocks in
their own model. The three chains use distinct class and ``product_block_name``
values so they can coexist in the registry within a single test session.
"""

from orchestrator.core.domain.base import ProductBlockModel, SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlock,
    NokiaFlexIlsBlockInactive,
    NokiaFlexIlsBlockProvisioning,
)


class LocationRouterBlockInactive(ProductBlockModel, product_block_name="LocationRouterBlock"):
    """Consumer-style product block with a has-a relation to the shipped location block."""

    for_the_optical_module: OpticalModuleLocationBlockInactive


class LocationRouterBlockProvisioning(LocationRouterBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """The provisioning variant of the consumer-style block."""

    for_the_optical_module: OpticalModuleLocationBlockProvisioning


class LocationRouterBlock(LocationRouterBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style block."""

    for_the_optical_module: OpticalModuleLocationBlock


class AbstractLocationRouterInactive(SubscriptionModel, is_base=True):
    """Abstract consumer-style subscription model composing the block."""

    router: LocationRouterBlockInactive


class AbstractLocationRouterProvisioning(
    AbstractLocationRouterInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """The provisioning variant of the consumer-style subscription model."""

    router: LocationRouterBlockProvisioning


class AbstractLocationRouter(AbstractLocationRouterProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style subscription model."""

    router: LocationRouterBlock


class NodeRouterBlockInactive(ProductBlockModel, product_block_name="TestNodeRouterBlock"):
    """Consumer-style product block with a has-a relation to the shipped Nokia FlexILS block."""

    for_the_optical_module: NokiaFlexIlsBlockInactive


class NodeRouterBlockProvisioning(NodeRouterBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """The provisioning variant of the consumer-style block."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    for_the_optical_module: NokiaFlexIlsBlockProvisioning


class NodeRouterBlock(NodeRouterBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style block."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    for_the_optical_module: NokiaFlexIlsBlock


class AbstractNodeRouterInactive(SubscriptionModel, is_base=True):
    """Abstract consumer-style subscription model composing the block."""

    router: NodeRouterBlockInactive


class AbstractNodeRouterProvisioning(AbstractNodeRouterInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """The provisioning variant of the consumer-style subscription model."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    router: NodeRouterBlockProvisioning


class AbstractNodeRouter(AbstractNodeRouterProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style subscription model."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    router: NodeRouterBlock


class CoherentPluggableRouterBlockInactive(ProductBlockModel, product_block_name="TestCoherentPluggableRouterBlock"):
    """Consumer-style product block with a has-a relation to the shipped Coherent Pluggable block."""

    for_the_optical_module: OpticalCoherentPluggableBlockInactive


class CoherentPluggableRouterBlockProvisioning(
    CoherentPluggableRouterBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """The provisioning variant of the consumer-style block."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    for_the_optical_module: OpticalCoherentPluggableBlockProvisioning


class CoherentPluggableRouterBlock(CoherentPluggableRouterBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """The active variant of the consumer-style block."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    for_the_optical_module: OpticalCoherentPluggableBlock


class AbstractCoherentPluggableRouterInactive(SubscriptionModel, is_base=True):
    """Abstract consumer-style subscription model composing the block."""

    router: CoherentPluggableRouterBlockInactive


class AbstractCoherentPluggableRouterProvisioning(
    AbstractCoherentPluggableRouterInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """The provisioning variant of the consumer-style subscription model."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    router: CoherentPluggableRouterBlockProvisioning


class AbstractCoherentPluggableRouter(
    AbstractCoherentPluggableRouterProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """The active variant of the consumer-style subscription model."""

    # pyrefly: ignore [bad-override-mutable-attribute]  # noqa: ERA001
    router: CoherentPluggableRouterBlock
