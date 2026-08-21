"""Modify Nokia Groove G30 Optical Node workflow.

This module ships the ready-to-use ``modify_optical_node_nokia_groove_g30``
workflow for the shipped Nokia Groove G30 product type, together with the
importable parts: the form generator (parameterized by the subscription model
and the attribute name of the composed block) and the step list that updates
and persists the Nokia Groove G30 node block found in the state under
``OPTICAL_NODE_BLOCK_STATE_KEY``. Consumers that keep the shipped product type
register the shipped workflow; consumers with their own model that has-a the
shipped block compose their own ``@modify_workflow`` with the parts.
"""

from collections.abc import Sequence

from pydantic_forms.types import FormGenerator, State, UUIDstr

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30BlockProvisioning,
)
from orchestrator.optical.products.product_types.optical_node.nokia_groove_g30 import OpticalNodeNokiaGrooveG30
from orchestrator.optical.utils.custom_types.dns import Pqdn
from orchestrator.optical.utils.custom_types.ip_address import IPAddress
from orchestrator.optical.workflows.optical_node.shared import (
    OPTICAL_NODE_BLOCK_STATE_KEY,
    load_optical_node_block,
    optical_node_modify_input_form,
    save_optical_node_block,
    update_optical_node_block_fields,
)


def modify_optical_node_nokia_groove_g30_form_generator(
    subscription_id: UUIDstr,
    subscription_model: type[SubscriptionModel] = OpticalNodeNokiaGrooveG30,
    block_field_name: str = "optical_node",
    extra_form_pages: Sequence[type[FormPage]] = (),
    extra_summary_fields: Sequence[str] = (),
) -> FormGenerator:
    """Generate the initial input form for modifying a Nokia Groove G30 Optical Node.

    Args:
        subscription_id: The identifier of the subscription being modified.
        subscription_model: The ACTIVE subscription model class of the Optical Node product.
            Defaults to the shipped :class:`OpticalNodeNokiaGrooveG30`; consumers that
            compose the shipped block under a different attribute name pass their own
            model class here.
        block_field_name: Name of the attribute of the subscription model holding
            the Nokia Groove G30 node block. Consumers that compose the shipped
            block under a different attribute name pass their own attribute name here.
        extra_form_pages: Additional form pages shown before the summary form.
        extra_summary_fields: Extra field names to append to the summary.
    """
    yield from optical_node_modify_input_form(
        subscription_id,
        subscription_model=subscription_model,
        block_field_name=block_field_name,
        extra_form_pages=extra_form_pages,
        extra_summary_fields=extra_summary_fields,
    )


@step("Updating Nokia Groove G30 node block")
def update_optical_node_nokia_groove_g30_block(
    optical_node_block: NokiaGrooveG30BlockProvisioning,
    location_id: UUIDstr,
    pqdn: Pqdn,
    optical_management_ip: IPAddress | None = None,
    optical_loopback_ip: IPAddress | None = None,
) -> State:
    """Update the Nokia Groove G30 node block in the state from the modify-form keys.

    Args:
        optical_node_block: The Nokia Groove G30 node block in the state under
            ``OPTICAL_NODE_BLOCK_STATE_KEY`` (the provisioning variant, while
            the subscription is being modified).
        location_id: Subscription id of the Optical Location hosting the node.
        pqdn: PQDN of the node.
        optical_management_ip: Management IP through which the node can be reached directly.
        optical_loopback_ip: Loopback IP through which the node can be reached directly.
    """
    update_optical_node_block_fields(
        optical_node_block=optical_node_block,
        location_id=location_id,
        pqdn=pqdn,
        optical_management_ip=optical_management_ip,
        optical_loopback_ip=optical_loopback_ip,
    )

    return {OPTICAL_NODE_BLOCK_STATE_KEY: optical_node_block}


#: Modify steps operating on the Nokia Groove G30 node block in the state. The
#: block is persisted by the last step, because workflow steps reload the
#: subscription from the database and would otherwise lose the mutations.
MODIFY_NOKIA_GROOVE_G30_BLOCK_STEPS: StepList = (
    begin >> update_optical_node_nokia_groove_g30_block >> save_optical_node_block
)


@modify_workflow(initial_input_form=modify_optical_node_nokia_groove_g30_form_generator)
def modify_optical_node_nokia_groove_g30() -> StepList:
    """Workflow to modify an existing Nokia Groove G30 Optical Node subscription.

    The workflow is valid for the shipped :class:`OpticalNodeNokiaGrooveG30`
    product type only: it loads the block from the ``optical_node`` attribute
    of the shipped subscription models. Consumers with their own product type
    compose their own modify workflow with the shipped parts.
    """
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_optical_node_block
        >> MODIFY_NOKIA_GROOVE_G30_BLOCK_STEPS
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )


__all__ = [
    "MODIFY_NOKIA_GROOVE_G30_BLOCK_STEPS",
    "modify_optical_node_nokia_groove_g30",
    "modify_optical_node_nokia_groove_g30_form_generator",
    "update_optical_node_nokia_groove_g30_block",
]
