# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from orchestrator.db import db
from orchestrator.forms import FormPage
from orchestrator.services.processes import start_process
from orchestrator.services.products import get_product_by_name
from orchestrator.targets import Target
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, done, step, workflow
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from products.product_blocks.optical_device import DeviceType
from products.product_types.optical_device import OpticalDevice
from products.product_types.optical_fiber import OpticalFiber
from workflows.optical_device.shared import (
    multiple_optical_device_selector,
)

logger = get_logger(__name__)


def initial_input_form_generator() -> FormGenerator:
    optical_device_types = [
        DeviceType.ROADM,
    ]
    RoadmChoiceList = multiple_optical_device_selector(
        device_types=optical_device_types,
        prompt="Select all the ROADMs of which you want to validate the optical fibers",
    )

    class InputForm(FormPage):
        roadm_list: RoadmChoiceList

    user_input = yield InputForm
    user_input_dict = user_input.dict()
    return user_input_dict


@step("Retrieving Optical Fibers attached to ROADMs")
def retrieve_fibers(roadm_list: list[UUIDstr]) -> State:
    optical_fiber_product_id = get_product_by_name("optical_fiber").product_id
    subscriptions = set()
    for sub_id in roadm_list:
        roadm_sub = OpticalDevice.from_subscription(sub_id)
        roadm = roadm_sub.optical_device
        sub_instances_using_roadm = roadm.in_use_by
        for sub_instance in sub_instances_using_roadm:
            if sub_instance.subscription.product.product_id != optical_fiber_product_id:
                continue
            if sub_instance.subscription.status != SubscriptionLifecycle.ACTIVE:
                continue
            fiber_sub = OpticalFiber.from_subscription(sub_instance.subscription_id)
            fiber = fiber_sub.optical_fiber
            for device in (x.optical_device for x in fiber.terminations):
                if device == roadm:
                    continue
                if device.device_type in [DeviceType.ROADM, DeviceType.Amplifier]:
                    subscriptions.add(sub_instance.subscription_id)

    return {"optical_fiber_subscriptions": subscriptions}


@step("Starting validation sub-workflows")
def start_sub_workflows(optical_fiber_subscriptions: set[UUIDstr]) -> State:
    process_ids: list[UUIDstr] = []
    while optical_fiber_subscriptions:
        subscription_id = optical_fiber_subscriptions.pop()
        user_inputs = [{"subscription_id": str(subscription_id)}]
        with db.database_scope():
            process_id = start_process("validate_optical_fiber", user_inputs=user_inputs, user="SYSTEM")
            process_ids.append(process_id)

    return {"process_ids": process_ids}


@workflow(
    "Update passbands (validate) of Optical Fibers attached to a list of ROADMs",
    target=Target.SYSTEM,
    initial_input_form=initial_input_form_generator,
)
def bulk_validate_optical_fibers() -> StepList:
    return begin >> retrieve_fibers >> start_sub_workflows >> done
