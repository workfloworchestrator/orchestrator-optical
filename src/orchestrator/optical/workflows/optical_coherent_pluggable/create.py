"""Workflow to create an Optical Coherent Pluggable subscription."""

from pydantic import ConfigDict, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.products.product_blocks.optical_packet_node import AbstractOpticalPacketNodeBlockInactive
from orchestrator.optical.products.product_types.optical_coherent_pluggable import (
    OpticalCoherentPluggable,
    OpticalCoherentPluggableInactive,
    OpticalCoherentPluggablePartNumber,
    OpticalCoherentPluggableProvisioning,
)
from orchestrator.optical.products.product_types.optical_packet_node import AbstractOpticalPacketNodeInactive
from orchestrator.optical.workflows.shared import (
    active_subscription_selector_by_block_type,
    create_summary_form,
    subscription_from_subscription,
    subscriptions_by_product_type_and_instance_value,
)

logger = get_logger(__name__)


def subscription_description(subscription: OpticalCoherentPluggableInactive) -> str:
    """Generate subscription description for Coherent Pluggables."""
    pluggable = subscription.optical_coherent_pluggable
    host_node = pluggable.optical_port_host_node
    host_name = host_node.pqdn if host_node else "Unattached Host"
    part_number = subscription.optical_coherent_pluggable_part_number
    return f"{host_name} {pluggable.optical_port_name} ({part_number})"


def initial_input_form_generator(product_name: str) -> FormGenerator:
    """Initial input form for creating an Optical Coherent Pluggable."""
    packet_node_choice = active_subscription_selector_by_block_type(
        AbstractOpticalPacketNodeBlockInactive, prompt="Select an Optical Packet Node"
    )
    part_number_choice = Choice(
        "Select Optical Coherent Pluggable Part Number",
        [(item.value, item.value) for item in OpticalCoherentPluggablePartNumber],
    )

    class CreateOpticalCoherentPluggableForm(FormPage):
        model_config = ConfigDict(title=product_name)

        optical_packet_node_id: packet_node_choice
        optical_coherent_pluggable_part_number: part_number_choice
        optical_port_name: str
        optical_port_description: str | None = None
        optical_coherent_pluggable_firmware_version: str

        @model_validator(mode="after")
        def validate_unique_port_on_node(self) -> "CreateOpticalCoherentPluggableForm":
            node_sub = subscription_from_subscription(AbstractOpticalPacketNodeInactive, self.optical_packet_node_id)
            node_pqdn = node_sub.optical_packet_node.pqdn

            # Check if this port on the host node is already assigned
            existing_subs = subscriptions_by_product_type_and_instance_value(
                product_type="OpticalCoherentPluggable",
                resource_type="optical_port_name",
                value=self.optical_port_name,
                status=[
                    SubscriptionLifecycle.INITIAL,
                    SubscriptionLifecycle.PROVISIONING,
                    SubscriptionLifecycle.ACTIVE,
                ],
            )
            for sub in existing_subs:
                # The ACTIVE class is the most-derived subclass, so it can load INITIAL,
                # PROVISIONING and ACTIVE subscriptions (unlike the PROVISIONING class).
                pluggable_sub = OpticalCoherentPluggable.from_subscription(sub.subscription_id)
                if pluggable_sub.optical_coherent_pluggable.optical_port_host_node.pqdn == node_pqdn:
                    msg = (
                        f"Port {self.optical_port_name} on node {node_pqdn} "
                        f"is already occupied by subscription {sub.subscription_id}"
                    )
                    raise ValueError(msg)

            return self

    user_input = yield CreateOpticalCoherentPluggableForm
    user_input_dict = user_input.model_dump()

    summary_fields = [
        "optical_packet_node_id",
        "optical_coherent_pluggable_part_number",
        "optical_port_name",
        "optical_port_description",
        "optical_coherent_pluggable_firmware_version",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Construct Subscription model")
def construct_optical_coherent_pluggable_model(
    product: UUIDstr,
    optical_packet_node_id: UUIDstr,
    optical_coherent_pluggable_part_number: OpticalCoherentPluggablePartNumber,
    optical_port_name: str,
    optical_port_description: str | None,
    optical_coherent_pluggable_firmware_version: str,
) -> State:
    """Instantiate and populate the domain model for Optical Coherent Pluggable."""
    packet_node_sub = subscription_from_subscription(AbstractOpticalPacketNodeInactive, optical_packet_node_id)
    customer_id = str(packet_node_sub.optical_packet_node.location.owner_subscription_id)

    subscription = OpticalCoherentPluggableInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    subscription.optical_coherent_pluggable_part_number = optical_coherent_pluggable_part_number
    pluggable_block = subscription.optical_coherent_pluggable
    pluggable_block.optical_port_host_node = packet_node_sub.optical_packet_node
    pluggable_block.optical_port_name = optical_port_name
    pluggable_block.optical_port_description = optical_port_description
    pluggable_block.optical_coherent_pluggable_firmware_version = optical_coherent_pluggable_firmware_version

    subscription = OpticalCoherentPluggableProvisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )
    subscription.description = subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        "subscription_description": subscription.description,
    }


additional_steps = begin


@create_workflow(
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def create_optical_coherent_pluggable() -> StepList:
    """Workflow to create an Optical Coherent Pluggable."""
    return (
        begin
        >> construct_optical_coherent_pluggable_model
        >> store_process_subscription()
    )
