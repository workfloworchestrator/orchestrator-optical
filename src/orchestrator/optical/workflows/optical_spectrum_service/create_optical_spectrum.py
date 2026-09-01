"""Create Optical Spectrum Service Workflow."""

from collections.abc import Sequence
from typing import Annotated

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import Divider
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.hal.port import set_port_description
from orchestrator.optical.hal.spectrum import deploy_optical_circuit
from orchestrator.optical.products import ProductType
from orchestrator.optical.products.product_blocks.optical_node._abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlockInactive
from orchestrator.optical.products.product_types.optical_node._abstracts import _AbstractOpticalNode
from orchestrator.optical.products.product_types.optical_spectrum_service import (
    OpticalSpectrumInactive,
    OpticalSpectrumProvisioning,
)
from orchestrator.optical.utils.custom_types.frequencies import Frequency
from orchestrator.optical.workflows.customer import customer_choice_selector
from orchestrator.optical.workflows.optical_pipe.shared import multiple_optical_pipe_selector
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    NoOpticalPathFoundError,
    multiple_optical_node_selector,
    optical_client_port_selector,
    optical_node_selector_of_roles,
    optical_spectrum_path_selector,
    store_list_of_ports_into_spectrum_sections,
    update_used_passbands,
)
from orchestrator.optical.workflows.shared import create_summary_form

logger = get_logger(__name__)

ROADM_ROLES = [
    OpticalNodeRole.ROADM,
    OpticalNodeRole.TRANSPONDER_XOADM,
]

LINE_SYSTEM_ROLES = [
    OpticalNodeRole.ROADM,
    OpticalNodeRole.TRANSPONDER_XOADM,
    OpticalNodeRole.AMPLIFIER,
]


def subscription_description(subscription: SubscriptionModel) -> str:
    """Generate the subscription description for an Optical Spectrum service."""
    spectrum = getattr(subscription, "optical_spectrum_service", None)
    if spectrum and getattr(spectrum, "optical_spectrum_name", None):
        return f"{spectrum.optical_spectrum_name} ({subscription.product.name})"
    return subscription.product.name


def initial_input_form_generator(
    product_name: str,
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for creating an Optical Spectrum service.

    Args:
        product_name: Name of the product being created.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    NodeAChoice = optical_node_selector_of_roles(  # noqa: N806
        roles=ROADM_ROLES,
        prompt="This service connects this node: ",
    )
    NodeBChoice = optical_node_selector_of_roles(  # noqa: N806
        roles=ROADM_ROLES,
        prompt="...to this other node: ",
    )
    customer_choice = customer_choice_selector()

    class OpticalSpectrumInputForm(FormPage):
        """Form for inputting service name and min and max frequencies."""

        model_config = ConfigDict(title=product_name)

        customer_id: customer_choice
        optical_spectrum_name: str
        src_optical_device_id: NodeAChoice
        dst_optical_device_id: NodeBChoice
        frequency_min: Annotated[Frequency, Field(title="Start frequency (THz)")]
        frequency_max: Annotated[Frequency, Field(title="End frequency (THz)")]

        @model_validator(mode="after")
        def validate_frequencies(self) -> "OpticalSpectrumInputForm":
            if self.frequency_min > self.frequency_max:
                msg = "Max frequency must be greater than min frequency. Did you make a typo?"
                raise ValueError(msg)
            return self

        @model_validator(mode="after")
        def validate_separate_nodes(self) -> "OpticalSpectrumInputForm":
            if self.dst_optical_device_id == self.src_optical_device_id:
                msg = "Destination Optical Node cannot be the same as Source Optical Node"
                raise ValueError(msg)
            return self

    user_input = yield OpticalSpectrumInputForm
    user_input_dict = user_input.model_dump()

    sub_node_a = _AbstractOpticalNode.from_subscription(user_input_dict["src_optical_device_id"])
    optical_node_a = sub_node_a.optical_node
    sub_node_b = _AbstractOpticalNode.from_subscription(user_input_dict["dst_optical_device_id"])
    optical_node_b = sub_node_b.optical_node

    SrcOpticalPortSelector = optical_client_port_selector(  # noqa: N806
        user_input_dict["src_optical_device_id"],
        prompt=(
            f"Select the Add/Drop Port on {optical_node_a.management.optical_module_node_fqdn}."
            " Please be careful to select the correct port."
        ),
    )
    DstOpticalPortSelector = optical_client_port_selector(  # noqa: N806
        user_input_dict["dst_optical_device_id"],
        prompt=(
            f"Select the Add/Drop Port on {optical_node_b.management.optical_module_node_fqdn}."
            " Please be careful to select the correct port."
        ),
    )

    class OpticalSpectrumAddDropForm(FormPage):
        """Form for selecting source and destination add/drop ports."""

        model_config = ConfigDict(title=product_name)

        src_optical_port_name: SrcOpticalPortSelector
        dst_optical_port_name: DstOpticalPortSelector

    user_input = yield OpticalSpectrumAddDropForm
    user_input_dict.update(user_input.model_dump())

    ExcludeOpticalDeviceChoiceList = multiple_optical_node_selector(  # noqa: N806
        roles=LINE_SYSTEM_ROLES,
        prompt="Do *not* pass through these Optical Nodes",
    )

    ExcludeSpanChoiceList = multiple_optical_pipe_selector(  # noqa: N806
        ProductType.OPTICAL_FIBER_SPAN.value,
        prompt="Do *not* pass through these Optical Fiber Spans",
    )

    class OpticalSpectrumConstraintsForm(FormPage):
        """Form for specifying which optical devices or spans MUST NOT be traversed by the optical spectrum."""

        model_config = ConfigDict(title=product_name)

        exclude_devices_list: ExcludeOpticalDeviceChoiceList
        divider1: Divider
        exclude_fibers_list: ExcludeSpanChoiceList

    user_input = yield OpticalSpectrumConstraintsForm
    user_input_dict.update(user_input.model_dump())

    passband = (user_input_dict["frequency_min"], user_input_dict["frequency_max"])

    no_path_found_msg = (
        "No optical path found, please adjust the routing constraints"
        " in the previous step or validate fibers in the path."
    )
    try:
        PathChoice = optical_spectrum_path_selector(  # noqa: N806
            str(optical_node_a.subscription_instance_id),
            str(optical_node_b.subscription_instance_id),
            passband,
            user_input_dict["exclude_devices_list"],
            user_input_dict["exclude_fibers_list"],
            prompt=(
                "Select the optical path, if you don't see the desired path,"
                " adjust constraints in previous step or validate fibers along the path."
            ),
        )
    except NoOpticalPathFoundError:
        logger.exception(
            "No optical path found",
            src_optical_device_id=user_input_dict["src_optical_device_id"],
            dst_optical_device_id=user_input_dict["dst_optical_device_id"],
            passband=passband,
            exclude_devices_list=user_input_dict["exclude_devices_list"],
            exclude_fibers_list=user_input_dict["exclude_fibers_list"],
        )

        PathChoice = Choice(  # noqa: N806
            no_path_found_msg,
            [
                (no_path_found_msg, no_path_found_msg),
            ],
        )

    class OpticalSpectrumPathForm(FormPage):
        """Form for selecting the optical path."""

        model_config = ConfigDict(title="Optical Path")

        optical_path: PathChoice

        @model_validator(mode="after")
        def validate_data(self) -> "OpticalSpectrumPathForm":
            if self.optical_path == no_path_found_msg:
                msg = (
                    "No optical path found, please adjust the routing constraints "
                    "in the previous step or update fibers in the path."
                )
                raise ValueError(msg)
            return self

    user_input = yield OpticalSpectrumPathForm
    user_input_dict.update(user_input.model_dump())

    user_input_dict["optical_path"] = user_input_dict["optical_path"].split(";")

    summary_fields = [
        "customer_id",
        "optical_spectrum_name",
        "frequency_min",
        "frequency_max",
        "src_optical_device_id",
        "dst_optical_device_id",
        "src_optical_port_name",
        "dst_optical_port_name",
        "optical_path",
    ]
    for page in extra_form_pages:
        user_input_dict.update((yield page).model_dump())
    yield from create_summary_form(
        user_input_dict,
        product_name,
        summary_fields,
        extra_summary_fields=extra_summary_fields,
    )

    return user_input_dict


@step("Saving input data into the optical spectrum model")
def create_optical_spectrum_model(
    product: UUIDstr,
    customer_id: UUIDstr,
    optical_spectrum_name: str,
    frequency_min: Frequency,
    frequency_max: Frequency,
) -> State:
    """Create the initial subscription and populate the spectrum block with name and passband."""
    subscription = OpticalSpectrumInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )

    # set attributes: name and passband
    spectrum = subscription.optical_spectrum_service
    spectrum.optical_spectrum_name = optical_spectrum_name
    spectrum.optical_spectrum_passband = (frequency_min, frequency_max)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,  # necessary to be able to use older generic step functions
    }


@step("Dividing the optical path into single-device-family sections")
def divide_path_into_sections(
    subscription: OpticalSpectrumInactive,
    optical_path: list[UUIDstr],
    src_optical_port_name: str,
    dst_optical_port_name: str,
    src_optical_device_id: UUIDstr,
    dst_optical_device_id: UUIDstr,
) -> State:
    """Create the add/drop port blocks and split the optical path into vendor-specific sections."""
    src_device = _AbstractOpticalNode.from_subscription(src_optical_device_id).optical_node
    dst_device = _AbstractOpticalNode.from_subscription(dst_optical_device_id).optical_node
    spectrum = subscription.optical_spectrum_service

    # Source Add/Drop Port
    src_port = OlsAddDropPortBlockInactive.new(
        subscription_id=subscription.subscription_id,
        optical_port_name=src_optical_port_name,
        optical_port_host_node=src_device,
        optical_port_description=(
            f"Remotely connected to {dst_device.management.optical_module_node_fqdn}"
            f" {dst_optical_port_name} via {spectrum.optical_spectrum_name}. "
        ),
    )
    src_port.save(subscription_id=subscription.subscription_id, status=SubscriptionLifecycle.INITIAL)
    # Destination Add/Drop Port
    dst_port = OlsAddDropPortBlockInactive.new(
        subscription_id=subscription.subscription_id,
        optical_port_name=dst_optical_port_name,
        optical_port_host_node=dst_device,
        optical_port_description=(
            f"Remotely connected to {src_device.management.optical_module_node_fqdn}"
            f" {src_optical_port_name} via {spectrum.optical_spectrum_name}. "
        ),
    )
    dst_port.save(subscription_id=subscription.subscription_id, status=SubscriptionLifecycle.INITIAL)

    optical_path.insert(0, str(src_port.subscription_instance_id))
    optical_path.append(str(dst_port.subscription_instance_id))

    store_list_of_ports_into_spectrum_sections(optical_path, spectrum)

    return {
        "subscription": subscription,
    }


@step("Updating the subscription description")
def update_subscription_description(
    subscription: OpticalSpectrumProvisioning,
) -> State:
    """Update the subscription description with the spectrum name and the product name."""
    subscription.description = subscription_description(subscription)
    return {
        "subscription_description": subscription.description,
        "subscription": subscription,
    }


@step("Adding a description to the add/drop ports")
def configure_add_drop_ports_description(
    subscription: OpticalSpectrumProvisioning,
) -> State:
    """Set the port description on the device for the source and destination add/drop ports."""
    oss = subscription.optical_spectrum_service.optical_spectrum_sections
    src_port = oss[0].optical_spectrum_section_add_drop_ports[0]
    dst_port = oss[-1].optical_spectrum_section_add_drop_ports[-1]

    outputs = []
    for port in (src_port, dst_port):
        command_output = set_port_description(port, port.optical_port_description or "")
        outputs.append(command_output)

    return {"configuration_results": outputs, "subscription": subscription}


@step("Provisioning optical spectrum sections")
def provision_optical_sections(subscription: OpticalSpectrumProvisioning) -> State:
    """Deploy the optical circuit of every spectrum section on the devices."""
    spectrum = subscription.optical_spectrum_service
    passband = spectrum.optical_spectrum_passband
    spectrum_name = spectrum.optical_spectrum_name
    if spectrum_name is None:
        msg = "Optical spectrum name is not set"
        raise ValueError(msg)
    carrier = (int(0.5 * (passband[0] + passband[1])), passband[1] - passband[0])
    circuit_identifier = str(spectrum.subscription_instance_id)
    results = {}
    for section in spectrum.optical_spectrum_sections:
        src_node = section.optical_spectrum_section_add_drop_ports[0].optical_port_host_node
        results[(src_node.management.optical_module_node_vendor, src_node.management.optical_module_node_platform)] = (
            deploy_optical_circuit(
                src_node,
                section,
                spectrum_name,
                passband,
                carrier,
                label=spectrum_name,
                circuit_identifier=circuit_identifier,
            )
        )

    return {
        "configuration_results": results,
    }


@step("Updating the available passbands of any Open Line System port in the path")
def update_used_passbands_step(subscription: OpticalSpectrumProvisioning) -> State:
    """Refresh the used passbands of the Open Line System ports in the path from the devices."""
    spectrum = subscription.optical_spectrum_service
    update_used_passbands(spectrum)

    return {"subscription": subscription}


@create_workflow(initial_input_form=initial_input_form_generator)
def create_optical_spectrum() -> StepList:
    """Workflow to create a new Optical Spectrum service."""
    return (
        begin
        >> create_optical_spectrum_model
        >> store_process_subscription()
        >> divide_path_into_sections
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription_description
        >> configure_add_drop_ports_description
        >> provision_optical_sections
        >> update_used_passbands_step
    )
