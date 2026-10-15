"""Abstract implementation of Optical Node Product Blocks."""

from pydantic_forms.types import strEnum

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node_management import (
    OpticalModuleNodeManagementBlock,
    OpticalModuleNodeManagementBlockInactive,
    OpticalModuleNodeManagementBlockProvisioning,
)


class OpticalNodeRole(strEnum):
    """Roles of Optical Nodes.

    The role is always discovered from the device (never collected as user input) and
    is re-derived by every validate workflow, so it reports what the node's hardware
    makes of it. An Open Line System role exists in a bare and a transponder flavour:
    ``ROADM`` / ``FOADM`` describe an OLS node without transponder ports, while
    ``TRANSPONDER_ROADM`` / ``TRANSPONDER_FOADM`` describe a node carrying both
    transponder ports and a WSS / colorless add-drop respectively.
    """

    ROADM = "ROADM"
    FOADM = "FOADM"
    AMPLIFIER = "Amplifier"
    TRANSPONDER = "Transponder"
    TRANSPONDER_FOADM = "Transponder and FOADM"
    TRANSPONDER_ROADM = "Transponder and ROADM"
    IPODWDM = "IPoDWDM"


#: Roles forming an Open Add/Drop Multiplexer, in either flavour: the bare ones
#: (``ROADM``, ``FOADM``) and the ones that also carry transponder ports
#: (``TRANSPONDER_ROADM``, ``TRANSPONDER_FOADM``). These are the nodes of the line
#: system: they terminate the Optical Multiplexed Sections a path runs over, they host
#: the add/drop ports a circuit or a leased spectrum is terminated on, and their ports
#: are the ones that carry spectral occupation. Amplifiers are excluded because they
#: only sit between two endpoints and report no occupation of their own. Ordered,
#: because the role selectors build their prompt from these values.
OADM_ROLES: tuple[OpticalNodeRole, ...] = (
    OpticalNodeRole.ROADM,
    OpticalNodeRole.FOADM,
    OpticalNodeRole.TRANSPONDER_ROADM,
    OpticalNodeRole.TRANSPONDER_FOADM,
)

#: Roles of the Optical Nodes forming the line system, i.e. every node an optical path
#: may run through: the add/drop multiplexers of :data:`OADM_ROLES` plus the amplifiers,
#: which only ever sit *between* two endpoints. This is the group the path-routing
#: selectors offer as waypoints and as nodes to avoid; the endpoints themselves are
#: chosen from :data:`OADM_ROLES`.
LINE_SYSTEM_ROLES: tuple[OpticalNodeRole, ...] = (*OADM_ROLES, OpticalNodeRole.AMPLIFIER)

#: Roles valid as endpoints of a client digital service, i.e. roles whose node hosts
#: transponder ports. The bare OADM roles are excluded: without a transponder card
#: there is nothing to terminate a client service on.
TRANSCEIVER_ROLES: tuple[OpticalNodeRole, ...] = (
    OpticalNodeRole.TRANSPONDER,
    OpticalNodeRole.TRANSPONDER_ROADM,
    OpticalNodeRole.TRANSPONDER_FOADM,
    OpticalNodeRole.IPODWDM,
)


class AbstractOpticalNodeBlockInactive(ProductBlockModel):
    """Abstract implementation of an Optical Node that is inactive."""

    optical_node_role: OpticalNodeRole | None = None

    management: OpticalModuleNodeManagementBlockInactive
    location: OpticalModuleLocationBlockInactive


class AbstractOpticalNodeBlockProvisioning(
    AbstractOpticalNodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Abstract implementaiton of an Optical Node that is provisioning."""

    optical_node_role: OpticalNodeRole | None = None

    management: OpticalModuleNodeManagementBlockProvisioning
    location: OpticalModuleLocationBlockProvisioning


class AbstractOpticalNodeBlock(AbstractOpticalNodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Abstract implementation of an Optical Node."""

    optical_node_role: OpticalNodeRole

    management: OpticalModuleNodeManagementBlock
    location: OpticalModuleLocationBlock
