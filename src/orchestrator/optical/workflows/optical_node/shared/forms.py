"""Shared create form pages for Optical Nodes.

The Optical Node vendor create forms (Nokia FlexILS, Groove G30, GX G42) are
compositions of the same pages: one per composed block plus a vendor-specific
page for the vendors that need it. This module ships those shared pages:

* :func:`create_optical_node_location_form` — the ``location_id`` selector of
  the Optical Location composition block;
* :func:`create_optical_node_management_form` — the fields of the
  ``OpticalModuleNodeManagementBlock`` composition block: the node FQDN and the
  DCN loopback/interface IPs;
* :func:`create_optical_node_role_form` — the node role, for the vendors that
  collect it as user input (currently unused by the shipped vendors, which
  discover the role from the device).

The node role is discovered from the device for all shipped vendors, so the
role is not collected as user input.
"""

from typing import Annotated

from pydantic import ConfigDict, Field, model_validator

from orchestrator.core.forms import FormPage
from orchestrator.optical.utils.custom_types.dns import Fqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_location.shared import active_location_subscription_selector
from orchestrator.optical.workflows.optical_node.shared.create import (
    validate_management_ips_uniqueness,
    validate_optical_node_fqdn_uniqueness,
)


def create_optical_node_location_form(product_name: str) -> type[FormPage]:
    """Return the location FormPage of an Optical Node create form.

    The page collects the Optical Location composition block: the
    ``location_id`` of the subscription hosting the node. It is a building
    block shared by all the Optical Node vendor create forms.

    Args:
        product_name: Name of the product being created, used as the page title.

    Returns:
        The location FormPage of the shipped create form.
    """
    location_choice = active_location_subscription_selector()

    class CreateOpticalNodeLocationForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Location")

        location_id: location_choice

    return CreateOpticalNodeLocationForm


def create_optical_node_management_form(product_name: str, *, require_dcn_ip: bool = True) -> type[FormPage]:
    """Return the management FormPage of an Optical Node create form.

    The page collects the fields of the ``OpticalModuleNodeManagementBlock``
    composition block: the node FQDN and the DCN loopback/interface IPs through
    which the node can be reached. It is a building block shared by all the
    Optical Node vendor create forms. The page validates that the FQDN and the
    management IPs are not already in use by another Optical Node subscription.

    Args:
        product_name: Name of the product being created, used as the page title.
        require_dcn_ip: Require at least one of the two DCN IPs to be provided.
            The Groove G30 and GX G42 create forms require one; the FlexILS
            create form does not.

    Returns:
        The management FormPage of the shipped create form.
    """

    class CreateOpticalNodeManagementForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Management")

        optical_module_node_fqdn: Annotated[
            Fqdn,
            Field(title="FQDN of the Optical Node"),
        ]
        optical_module_node_dcn_loopback_ip: IPAddress | None = None
        optical_module_node_dcn_interface_ip: IPAddress | None = None

        @model_validator(mode="after")
        def validate_form(self) -> "CreateOpticalNodeManagementForm":
            """Raise if the DCN IPs are missing or the values are not unique."""
            if require_dcn_ip and not (
                self.optical_module_node_dcn_loopback_ip or self.optical_module_node_dcn_interface_ip
            ):
                msg = "At least one of DCN loopback IP or DCN interface IP must be provided."
                raise ValueError(msg)

            validate_optical_node_fqdn_uniqueness(self.optical_module_node_fqdn)
            validate_management_ips_uniqueness(
                [
                    ip
                    for ip in (self.optical_module_node_dcn_loopback_ip, self.optical_module_node_dcn_interface_ip)
                    if ip is not None
                ]
            )
            return self

    return CreateOpticalNodeManagementForm
