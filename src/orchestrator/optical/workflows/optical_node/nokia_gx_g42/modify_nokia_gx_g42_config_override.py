"""Override the configuration of a Nokia GX G42 Optical Node.

Ships the ready-to-use ``modify_optical_node_nokia_gx_g42_config_override`` workflow for the
shipped Nokia GX G42 product type: the NOC changes the configuration of the node by hand with
``<marker> path: value`` lines (see
:mod:`orchestrator.optical.workflows.optical_node.shared.config_override`). Consumers with
their own product type compose the same workflow from the shared form pages and step.
"""

from pydantic_forms.types import FormGenerator, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.workflow import StepList, begin
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_types.optical_node.nokia_gx_g42 import OpticalNodeNokiaGxG42Subscription
from orchestrator.optical.workflows.optical_node.shared import load_optical_node_block
from orchestrator.optical.workflows.optical_node.shared.config_override import (
    apply_optical_node_config_override,
    config_override_form_pages,
)
from orchestrator.optical.workflows.shared import retryable_form


@retryable_form
def modify_optical_node_nokia_gx_g42_config_override_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalNodeNokiaGxG42Subscription,
    block_field_name: str = "optical_node",
) -> FormGenerator:
    """Generate the configuration override form of a Nokia GX G42 Optical Node subscription."""
    subscription = subscription_model.from_subscription(subscription_id)
    user_input = yield from config_override_form_pages(getattr(subscription, block_field_name))
    return user_input | {"subscription": subscription}


@modify_workflow(initial_input_form=modify_optical_node_nokia_gx_g42_config_override_form_generator)
def modify_optical_node_nokia_gx_g42_config_override() -> StepList:
    """Workflow to override the configuration of a Nokia GX G42 Optical Node."""
    return begin >> load_optical_node_block >> apply_optical_node_config_override


__all__ = [
    "modify_optical_node_nokia_gx_g42_config_override",
    "modify_optical_node_nokia_gx_g42_config_override_form_generator",
]
