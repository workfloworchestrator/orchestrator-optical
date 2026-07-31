"""Shared modification steps for Optical Nodes."""

from pydantic_forms.types import State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import step
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_types.optical_location import AbstractOpticalLocation
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_node.shared.create import optical_node_subscription_description


def update_abstract_optical_node_fields(
    optical_node_block,
    location_id: UUIDstr | None = None,
    optical_node_role: OpticalNodeRole | None = None,
    pqdn: Pqdn | None = None,
    optical_management_ip_list: list[IPAddress] | None = None,
    optical_node_software_version: str | None = None,
) -> None:
    """Update abstract fields on an optical node block if new values are provided."""
    if location_id:
        location_sub = AbstractOpticalLocation.from_subscription(location_id)
        optical_node_block.location = location_sub.optical_location
    if optical_node_role:
        optical_node_block.optical_node_role = optical_node_role
    if pqdn:
        optical_node_block.pqdn = pqdn
    if optical_management_ip_list:
        optical_node_block.optical_management_ip_list = optical_management_ip_list
    if optical_node_software_version is not None:
        optical_node_block.optical_node_software_version = optical_node_software_version


@step("Updating subscription description")
def update_optical_node_subscription_description(subscription: SubscriptionModel) -> State:
    """Update the description of the Optical Node subscription."""
    subscription.description = optical_node_subscription_description(subscription)
    return {"subscription": subscription}
