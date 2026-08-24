"""Create Optical Leased Spectrum Workflow.

The subscription model has no dedicated provider field: the ``provider_name``
collected by the form is always persisted by prefixing it to the
``optical_pipe_name`` (``"<provider> <circuit id or default>"``), so that no
input is silently dropped.
"""

from collections.abc import Sequence
from typing import cast
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
    get_device_client_ports_names,
    get_device_line_ports_names,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlockInactive,
    OpticalNodeRole,
)
from orchestrator.optical.products.product_blocks.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_port.ols_line import OlsLinePortBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_port.unions import LeasedSpectrumPortBlockInactive
from orchestrator.optical.products.product_types.optical_pipe.leased_spectrum import (
    OpticalLeasedSpectrumInactive,
    OpticalLeasedSpectrumProvisioning,
)
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_pipe.shared import (
    create_pipe_summary_form,
    default_pipe_identifier,
    leased_spectrum_port_block_class,
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
    """Form generator for creating an Optical Leased Spectrum pipe.

    Args:
        product_name: Name of the product being created.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    node_choice = optical_node_selector(prompt="This leased spectrum connects this node:")
    customer_choice = customer_choice_selector()

    class CreateLeasedSpectrumForm1(FormPage):
        model_config = ConfigDict(title=product_name)

        customer_id: customer_choice
        node_a_id: node_choice
        node_b_id: node_choice

        @model_validator(mode="after")
        def validate_distinct_nodes(self) -> "CreateLeasedSpectrumForm1":
            if self.node_a_id == self.node_b_id:
                msg = "The two ends of a leased spectrum pipe must be on different nodes."
                raise ValueError(msg)
            return self

    user_input_1 = yield CreateLeasedSpectrumForm1
    user_input_dict = user_input_1.model_dump()

    node_a_block = node_block_from_subscription(user_input_dict["node_a_id"])
    node_b_block = node_block_from_subscription(user_input_dict["node_b_id"])

    port_a_choice = unused_node_port_selector(
        user_input_dict["node_a_id"],
        leased_spectrum_ports_of_node(node_a_block),
        prompt=f"Select an unused line or add/drop port on {node_a_block.pqdn}",
    )
    port_b_choice = unused_node_port_selector(
        user_input_dict["node_b_id"],
        leased_spectrum_ports_of_node(node_b_block),
        prompt=f"Select an unused line or add/drop port on {node_b_block.pqdn}",
    )

    class CreateLeasedSpectrumForm2(FormPage):
        model_config = ConfigDict(title=f"{product_name} - Terminations")

        provider_name: str = Field(..., title="Third-Party Provider Name", min_length=1)
        optical_pipe_name: str | None = Field(
            None,
            title="Leased Spectrum Identifier",
            description="Circuit ID or provider reference. Leave empty to use the default "
            "'<node A> <port A> --- <node B> <port B>'. The provider name is always prefixed.",
        )
        port_a_name: port_a_choice
        port_b_name: port_b_choice

    user_input_2 = yield CreateLeasedSpectrumForm2
    user_input_dict.update(user_input_2.model_dump())

    user_input_dict["optical_pipe_name"] = user_input_dict["optical_pipe_name"] or default_pipe_identifier(
        node_a_block, user_input_dict["port_a_name"], node_b_block, user_input_dict["port_b_name"]
    )

    summary_fields = [
        "customer_id",
        "provider_name",
        "optical_pipe_name",
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


def leased_spectrum_ports_of_node(node_block: AbstractOpticalNodeBlockInactive) -> list[str]:
    """Return the ports of a node that can terminate a leased spectrum pipe.

    On a Nokia FlexILS node only the OLS add/drop (SCG) ports are selectable: the
    OTS ports are OLS line ports that the FlexILS HAL cannot configure end-to-end
    for a leased spectrum pipe. On Groove G30 and GX G42 nodes only the line ports
    are selectable; the client ports are not part of the leased spectrum port block
    union.
    """
    if vendor_of(node_block) == Vendor.FLEXILS:
        return get_device_client_ports_names(node_block)
    return list(dict.fromkeys(get_device_line_ports_names(node_block)))


@step("Construct Leased Spectrum Model")
def construct_leased_spectrum_model(
    product: UUIDstr,
    customer_id: UUIDstr,
    provider_name: str,
    node_a_id: UUIDstr,
    node_b_id: UUIDstr,
    port_a_name: str,
    port_b_name: str,
    optical_pipe_name: str,
) -> State:
    """Construct the OpticalLeasedSpectrum domain subscription model."""
    node_a_block = node_block_from_subscription(node_a_id)
    node_b_block = node_block_from_subscription(node_b_id)

    subscription_id = uuid4()
    client_ports_a = get_device_client_ports_names(node_a_block)
    client_ports_b = get_device_client_ports_names(node_b_block)
    port_a = new_pipe_port_block(
        subscription_id,
        node_a_block,
        port_a_name,
        f"Physically connected to {node_b_block.pqdn} {port_b_name}.",
        leased_spectrum_port_block_class(node_a_block, port_a_name, client_ports_a),
    )
    port_b = new_pipe_port_block(
        subscription_id,
        node_b_block,
        port_b_name,
        f"Physically connected to {node_a_block.pqdn} {port_a_name}.",
        leased_spectrum_port_block_class(node_b_block, port_b_name, client_ports_b),
    )

    pipe_block = OpticalLeasedSpectrumBlockInactive.new(
        subscription_id=subscription_id,
        optical_pipe_terminations=cast(list[LeasedSpectrumPortBlockInactive], [port_a, port_b]),
    )
    provider_name = provider_name.strip()
    if provider_name:
        optical_pipe_name = f"{provider_name} {optical_pipe_name}"
    pipe_block.optical_pipe_name = optical_pipe_name

    subscription = new_optical_pipe_subscription(OpticalLeasedSpectrumInactive, product, customer_id, pipe_block)
    subscription = OpticalLeasedSpectrumProvisioning.from_other_lifecycle(
        subscription, SubscriptionLifecycle.PROVISIONING
    )
    subscription.description = optical_pipe_subscription_description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
        "subscription_description": subscription.description,
    }


@step("Configure Leased Spectrum Terminations")
def configure_leased_spectrum_terminations(subscription: OpticalLeasedSpectrumProvisioning) -> State:
    """Configure the terminating ports of the leased spectrum pipe on the devices."""
    port_a, port_b = subscription.optical_pipe.optical_pipe_terminations
    host_node_a = port_a.optical_port_host_node
    host_node_b = port_b.optical_port_host_node
    if not isinstance(host_node_a, AbstractOpticalNodeBlockInactive) or not isinstance(
        host_node_b, AbstractOpticalNodeBlockInactive
    ):
        msg = "Leased spectrum terminations must be hosted on Optical Nodes"
        raise TypeError(msg)
    if vendor_of(host_node_b) == Vendor.FLEXILS and vendor_of(host_node_a) != Vendor.FLEXILS:
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
def retrieve_leased_spectrum_used_passbands(subscription: OpticalLeasedSpectrumProvisioning) -> State:
    """Refresh the passbands in use on the terminating ports from the devices."""
    for port in subscription.optical_pipe.optical_pipe_terminations:
        if not isinstance(port, OlsAddDropPortBlockProvisioning | OlsLinePortBlockProvisioning):
            continue
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
def create_leased_spectrum() -> StepList:
    """Workflow to create a new Optical Leased Spectrum pipe."""
    return (
        begin
        >> construct_leased_spectrum_model
        >> store_process_subscription()
        >> configure_leased_spectrum_terminations
        >> retrieve_leased_spectrum_used_passbands
    )
