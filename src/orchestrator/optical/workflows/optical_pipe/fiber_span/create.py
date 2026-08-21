"""Create Optical Fiber Span Workflow."""

from collections.abc import Sequence
from uuid import uuid4

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.hal.optical_node import Vendor, retrieve_ports_spectral_occupations, vendor_of
from orchestrator.optical.hal.optical_port import (
    configure_termination_when_attaching_new_fiber,
    get_device_line_ports_names,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_span import OpticalFiberSpanBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlockInactive
from orchestrator.optical.products.product_types.optical_pipe.fiber_span import (
    OpticalFiberSpanInactive,
    OpticalFiberSpanProvisioning,
)
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_pipe.shared import (
    create_pipe_summary_form,
    default_pipe_identifier,
    new_optical_pipe_subscription,
    new_pipe_port_block,
    node_block_from_subscription,
    optical_node_selector,
    optical_pipe_subscription_description,
    unused_node_port_selector,
)

logger = get_logger(__name__)


def initial_input_form_generator(
    product_name: str,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Form generator for creating an Optical Fiber Span.

    Args:
        product_name: Name of the product being created.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    node_choice = optical_node_selector(prompt="This fiber span connects this node:")
    customer_choice = customer_choice_selector()

    class CreateFiberSpanForm1(FormPage):
        model_config = ConfigDict(title=product_name)

        customer_id: customer_choice
        node_a_id: node_choice
        node_b_id: node_choice

        @model_validator(mode="after")
        def validate_distinct_nodes(self) -> "CreateFiberSpanForm1":
            if self.node_a_id == self.node_b_id:
                msg = "The two ends of a fiber span must be on different nodes."
                raise ValueError(msg)
            return self

    user_input_1 = yield CreateFiberSpanForm1
    user_input_dict = user_input_1.model_dump()

    node_a_block = node_block_from_subscription(user_input_dict["node_a_id"])
    node_b_block = node_block_from_subscription(user_input_dict["node_b_id"])

    port_a_choice = unused_node_port_selector(
        user_input_dict["node_a_id"],
        get_device_line_ports_names(node_a_block),
        prompt=f"Select an unused line port on {node_a_block.pqdn}",
    )
    port_b_choice = unused_node_port_selector(
        user_input_dict["node_b_id"],
        get_device_line_ports_names(node_b_block),
        prompt=f"Select an unused line port on {node_b_block.pqdn}",
    )

    class CreateFiberSpanForm2(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Terminations")

        optical_pipe_identifier: str | None = Field(
            None,
            title="Fiber Span Identifier",
            description="Unique span ID or code. Leave empty to use the default 'node A port A --- node B port B'.",
        )
        port_a_name: port_a_choice
        port_b_name: port_b_choice

    user_input_2 = yield CreateFiberSpanForm2
    user_input_dict.update(user_input_2.model_dump())

    user_input_dict["optical_pipe_identifier"] = user_input_dict["optical_pipe_identifier"] or default_pipe_identifier(
        node_a_block, user_input_dict["port_a_name"], node_b_block, user_input_dict["port_b_name"]
    )

    summary_fields = [
        "customer_id",
        "optical_pipe_identifier",
        "node_a_id",
        "port_a_name",
        "node_b_id",
        "port_b_name",
    ]
    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())
    yield from create_pipe_summary_form(
        user_input_dict,
        product_name,
        summary_fields,
        extra_summary_fields=extra_summary_fields,
    )

    return user_input_dict


@step("Construct Fiber Span Model")
def construct_fiber_span_model(
    product: UUIDstr,
    customer_id: UUIDstr,
    node_a_id: UUIDstr,
    node_b_id: UUIDstr,
    port_a_name: str,
    port_b_name: str,
    optical_pipe_identifier: str,
) -> State:
    """Construct the OpticalFiberSpan domain subscription model."""
    node_a_block = node_block_from_subscription(node_a_id)
    node_b_block = node_block_from_subscription(node_b_id)

    subscription_id = uuid4()
    port_a = new_pipe_port_block(
        subscription_id,
        node_a_block,
        port_a_name,
        f"Physically connected to {node_b_block.pqdn} {port_b_name}.",
        OlsLinePortBlockInactive,
    )
    port_b = new_pipe_port_block(
        subscription_id,
        node_b_block,
        port_b_name,
        f"Physically connected to {node_a_block.pqdn} {port_a_name}.",
        OlsLinePortBlockInactive,
    )

    pipe_block = OpticalFiberSpanBlockInactive.new(
        subscription_id=subscription_id,
        optical_pipe_terminations=[port_a, port_b],
    )
    pipe_block.optical_pipe_identifier = optical_pipe_identifier

    subscription = new_optical_pipe_subscription(OpticalFiberSpanInactive, product, customer_id, pipe_block)
    subscription = OpticalFiberSpanProvisioning.from_other_lifecycle(subscription, SubscriptionLifecycle.PROVISIONING)
    subscription.description = optical_pipe_subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        "subscription_description": subscription.description,
    }


@step("Configure Fiber Span Terminations")
def configure_span_terminations(subscription: OpticalFiberSpanProvisioning) -> State:
    """Configure the terminating line ports of the fiber span on the devices."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    if (
        vendor_of(port_b.optical_port_host_node) == Vendor.FLEXILS
        and vendor_of(port_a.optical_port_host_node) != Vendor.FLEXILS
    ):
        # Configure the FlexILS side first: its configuration references the remote node.
        port_a, port_b = port_b, port_a

    configuration_results = {
        f"{port_a.optical_port_host_node.pqdn} {port_a.optical_port_name}": (
            configure_termination_when_attaching_new_fiber(port_a, port_b)
        ),
        f"{port_b.optical_port_host_node.pqdn} {port_b.optical_port_name}": (
            configure_termination_when_attaching_new_fiber(port_b, port_a)
        ),
    }
    return {"configuration_results": configuration_results, "subscription": subscription}


@step("Retrieve Used Passbands")
def retrieve_span_used_passbands(subscription: OpticalFiberSpanProvisioning) -> State:
    """Refresh the passbands in use on the terminating ports from the devices."""
    for port in subscription.optical_pipe.optical_pipe_terminations:
        host_node = port.optical_port_host_node
        if host_node.optical_node_role not in (
            OpticalNodeRole.ROADM,
            OpticalNodeRole.TRANSPONDER_XOADM,
            OpticalNodeRole.AMPLIFIER,
        ):
            continue
        if port.optical_port_name is None:
            msg = f"Optical port block of {host_node.pqdn} has no port name"
            raise ValueError(msg)
        port.optical_passbands = retrieve_ports_spectral_occupations(host_node).get(port.optical_port_name, [])
    return {"subscription": subscription}


@create_workflow(initial_input_form=initial_input_form_generator)
def create_fiber_span() -> StepList:
    """Workflow to create a new Optical Fiber Span."""
    return (
        begin
        >> construct_fiber_span_model
        >> store_process_subscription()
        >> configure_span_terminations
        >> retrieve_span_used_passbands
    )
