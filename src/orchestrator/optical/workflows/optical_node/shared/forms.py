"""Shared create and modify form pages for Optical Nodes.

The Optical Node vendor forms (Nokia FlexILS, Groove G30, GX G42) are
compositions of the same pages: one per composed block plus a vendor-specific
page for the vendors that need it. The create forms only ask how to reach the
node; what the node knows about itself (name, role, software version, FlexILS
GMPLS ID) is read from it while the form is filled in. This module ships those
shared pages:

* :func:`create_optical_node_location_form` — the ``location_instance_id`` selector of
  the Optical Location composition block of the create form;
* :func:`create_optical_node_management_form` — the management loopback/interface
  IPs through which the node is reached;
* :func:`discover_new_optical_node` — not a page: connects to the node being
  created and reads its name, role and software version;
* :func:`create_optical_node_identity_form` — the node name, prefilled with the
  name read from the device, next to what else the device reported;
* :func:`create_optical_node_role_form` — the node role, for the vendors that
  collect it as user input (currently unused by the shipped vendors, which
  discover the role from the device);
* :func:`modify_optical_node_management_form` — the management IPs of the
  modify form, prefilled with the current block values;
* :func:`modify_optical_node_identity_form` — the identity page of the modify
  form: the node is read again and the name prefilled as in the create form.
"""

from typing import Annotated

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import UUIDstr

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import Label
from orchestrator.optical.db import location_block_from_instance
from orchestrator.optical.hal.node import OpticalNodeDiscovery, discover_optical_node
from orchestrator.optical.products.product_blocks.optical_node.abstracts import AbstractOpticalNodeBlock
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.utils.custom_types.node_name import OpticalNodeName
from orchestrator.optical.workflows.optical_location.shared import active_location_instance_selector
from orchestrator.optical.workflows.optical_node.shared.create import (
    validate_management_ips_uniqueness,
    validate_optical_node_name_uniqueness,
)


def create_optical_node_location_form(product_name: str) -> type[FormPage]:
    """Return the location FormPage of an Optical Node create form.

    The page collects the Optical Location composition block: the
    ``location_instance_id`` of the block hosting the node. It is a building
    block shared by all the Optical Node vendor create forms.

    Args:
        product_name: Name of the product being created, used as the page title.

    Returns:
        The location FormPage of the shipped create form.
    """
    location_choice = active_location_instance_selector()

    class CreateOpticalNodeLocationForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Location")

        location_instance_id: location_choice

    return CreateOpticalNodeLocationForm


def create_optical_node_management_form(product_name: str, *, require_dcn_ip: bool = True) -> type[FormPage]:
    """Return the management FormPage of an Optical Node create form.

    The page collects how the node is reached: the management loopback/interface
    IPs of the ``OpticalModuleNodeManagementBlock`` composition block. It is a
    building block shared by all the Optical Node vendor create forms. The page
    validates that the management IPs are not already in use by another
    Optical Node subscription. The node name is not asked here: it is read
    from the device (:func:`discover_new_optical_node`) and confirmed on the
    identity page (:func:`create_optical_node_identity_form`).

    Args:
        product_name: Name of the product being created, used as the page title.
        require_dcn_ip: Require at least one of the two management IPs to be provided.
            The Groove G30 and GX G42 create forms require one; the FlexILS
            create form does not (a node without one is reached through a GNE).

    Returns:
        The management FormPage of the shipped create form.
    """

    class CreateOpticalNodeManagementForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Management")

        optical_module_node_management_loopback_ip: IPAddress | None = None
        optical_module_node_management_ip: IPAddress | None = None

        @model_validator(mode="after")
        def validate_form(self) -> "CreateOpticalNodeManagementForm":
            """Raise if the management IPs are missing or the values are not unique."""
            if require_dcn_ip and not (
                self.optical_module_node_management_loopback_ip or self.optical_module_node_management_ip
            ):
                msg = "At least one of the management loopback IP or the management IP must be provided."
                raise ValueError(msg)

            validate_management_ips_uniqueness(
                [
                    ip
                    for ip in (self.optical_module_node_management_loopback_ip, self.optical_module_node_management_ip)
                    if ip is not None
                ]
            )
            return self

    return CreateOpticalNodeManagementForm


def discover_new_optical_node(
    vendor: Vendor,
    platform: Platform,
    *,
    location_instance_id: UUIDstr | None = None,
    optical_module_node_management_loopback_ip: IPAddress | None = None,
    optical_module_node_management_ip: IPAddress | None = None,
    optical_flexils_target_id: str | None = None,
) -> OpticalNodeDiscovery:
    """Connect to the node being created and read its name, role and software version.

    Call it from a create form generator between the page collecting how the
    node is reached and :func:`create_optical_node_identity_form`. Inside a
    generator decorated with ``retryable_form`` an unreachable node is reported
    as a validation error of the page just submitted, so the user can correct
    the address and submit again. The form is replayed on every submit, so the
    node is read again on each of the following ones.

    Args:
        vendor: Vendor of the node.
        platform: Platform of the node.
        location_instance_id: Subscription instance id of the Optical Location
            block hosting the node (used to find a GNE for a FlexILS node
            without a DCN IP).
        optical_module_node_management_loopback_ip: Management loopback IP of the node.
        optical_module_node_management_ip: Management (interface) IP of the node.
        optical_flexils_target_id: Target ID of a FlexILS node.

    Returns:
        What the node reported.

    Raises:
        ValueError: If the node cannot be reached, identified or queried.
    """
    return discover_optical_node(
        vendor,
        platform,
        dcn_loopback_ip=optical_module_node_management_loopback_ip,
        dcn_interface_ip=optical_module_node_management_ip,
        flexils_target_id=optical_flexils_target_id,
        location=location_block_from_instance(location_instance_id) if location_instance_id else None,
    )


def create_optical_node_identity_form(product_name: str, discovery: OpticalNodeDiscovery) -> type[FormPage]:
    """Return the identity FormPage of an Optical Node create form.

    The page shows what the device reported (:func:`discover_new_optical_node`)
    and collects the node name, prefilled with the name read from the device:
    the user confirms it or types another one (e.g. a fully qualified domain
    name). The name is how the node is shown in subscription descriptions,
    messages and far-end device labels; it is never used to reach the node.
    The page validates that the name is not already in use by another Optical
    Node subscription.

    Args:
        product_name: Name of the product being created, used as the page title.
        discovery: What the device reported.

    Returns:
        The identity FormPage of the shipped create form.
    """
    return _optical_node_identity_form(f"{product_name} - Name", discovery)


def modify_optical_node_identity_form(
    node: AbstractOpticalNodeBlock,
    discovery: OpticalNodeDiscovery,
    *,
    exclude_subscription_id: UUIDstr | None = None,
) -> type[FormPage]:
    """Return the identity FormPage of an Optical Node modify form.

    The page is the one of the create form (:func:`create_optical_node_identity_form`),
    read again from the device: the name is prefilled with the name the device
    reports now (the stored name when the device has none), and the page tells
    the stored name when the two differ, so a name typed by hand at creation is
    kept by typing it again. The page validates that the name is not in use by
    another Optical Node subscription, excluding the subscription being modified.

    Args:
        node: The Optical Node block being modified.
        discovery: What the device reported.
        exclude_subscription_id: Identifier of the subscription being modified,
            whose own node block is not a conflict. Defaults to the owner
            subscription of the block.

    Returns:
        The identity FormPage of the shipped modify form.
    """
    exclude = exclude_subscription_id if exclude_subscription_id is not None else str(node.owner_subscription_id)
    return _optical_node_identity_form(
        "Name",
        discovery,
        current_name=node.management.optical_module_node_name,
        exclude_subscription_id=exclude,
    )


def _optical_node_identity_form(
    title: str,
    discovery: OpticalNodeDiscovery,
    *,
    current_name: str | None = None,
    exclude_subscription_id: UUIDstr | None = None,
) -> type[FormPage]:
    """Return the identity FormPage shared by the create and modify forms (see the public factories)."""
    reported = [f"role {discovery.role.value}", f"software version {discovery.software_version}"]
    if discovery.flexils_gmpls_id:
        reported.append(f"GMPLS ID {discovery.flexils_gmpls_id}")
    if discovery.name:
        about_name = "Its name is prefilled below; change it if needed."
    elif current_name:
        about_name = "It has no name configured: the current name is kept below."
    else:
        about_name = "It has no name configured."
    if current_name and discovery.name and current_name != discovery.name:
        about_name += f" The current name is {current_name}."
    default_name = discovery.name or current_name
    field_title = "Name of the Optical Node"
    name_field = Field(default=default_name, title=field_title) if default_name else Field(title=field_title)

    class OpticalNodeIdentityForm(FormPage):
        model_config = ConfigDict(title=title)

        discovered: Label = f"The node reports: {', '.join(reported)}. {about_name}"
        optical_module_node_name: Annotated[OpticalNodeName, name_field]

        @model_validator(mode="after")
        def validate_form(self) -> "OpticalNodeIdentityForm":
            """Raise if the node name is already in use by another subscription."""
            validate_optical_node_name_uniqueness(
                self.optical_module_node_name, exclude_subscription_id=exclude_subscription_id
            )
            return self

    return OpticalNodeIdentityForm


def modify_optical_node_management_form(
    node: AbstractOpticalNodeBlock,
    *,
    exclude_subscription_id: UUIDstr | None = None,
    require_dcn_ip: bool = True,
) -> type[FormPage]:
    """Return the management FormPage of an Optical Node modify form.

    The page collects the fields of the ``OpticalModuleNodeManagementBlock``
    composition block: the management loopback/interface IPs through which the
    node is reached (the node name is on the identity page,
    :func:`modify_optical_node_identity_form`, read again from the device). It is
    prefilled with the current values of the block, so unchanged fields
    remain intact. Either IP can be deleted by ticking its ``delete_*``
    checkbox, which sets the IP to ``None`` in the emitted state. The page
    validates that the (non-deleted) management IPs are not
    already in use by another Optical Node subscription, excluding the
    subscription being modified, and — when ``require_dcn_ip`` is set — that at
    least one management IP remains after the requested deletions. It is a building
    block shared by all the Optical Node vendor modify forms.

    Args:
        node: The Optical Node block being modified.
        exclude_subscription_id: Identifier of the subscription being modified,
            whose own node block is not a conflict. Defaults to the owner
            subscription of the block.
        require_dcn_ip: Require at least one of the two management IPs to remain after
            the requested deletions. The FlexILS modify form does not require
            one (mirroring its create form); Groove G30 and GX G42 do.

    Returns:
        The management FormPage of the shipped modify form.
    """
    exclude = exclude_subscription_id if exclude_subscription_id is not None else str(node.owner_subscription_id)

    class ModifyOpticalNodeManagementForm(FormPage):
        instruction: Label = (
            "Modify the Optical Node fields. Unchanged fields will remain intact. "
            "Tick a 'Delete ...' checkbox to remove the corresponding management IP."
        )
        optical_module_node_management_loopback_ip: IPAddress | None = (
            node.management.optical_module_node_management_loopback_ip
        )
        optical_module_node_management_ip: IPAddress | None = node.management.optical_module_node_management_ip
        delete_optical_module_node_management_loopback_ip: bool = Field(
            default=False,
            title="Delete management loopback IP",
            description="Tick to remove the management loopback IP from the node.",
        )
        delete_optical_module_node_management_ip: bool = Field(
            default=False,
            title="Delete management (interface) IP",
            description="Tick to remove the management (interface) IP from the node.",
        )

        @model_validator(mode="after")
        def validate_form(self) -> "ModifyOpticalNodeManagementForm":
            """Apply the deletions, then require a remaining management IP and unique values."""
            if self.delete_optical_module_node_management_loopback_ip:
                self.optical_module_node_management_loopback_ip = None
            if self.delete_optical_module_node_management_ip:
                self.optical_module_node_management_ip = None
            if require_dcn_ip and not (
                self.optical_module_node_management_loopback_ip or self.optical_module_node_management_ip
            ):
                msg = "At least one of the management loopback IP or the management IP must be provided."
                raise ValueError(msg)
            validate_management_ips_uniqueness(
                [
                    ip
                    for ip in (self.optical_module_node_management_loopback_ip, self.optical_module_node_management_ip)
                    if ip is not None
                ],
                exclude_subscription_id=exclude,
            )
            return self

    return ModifyOpticalNodeManagementForm
