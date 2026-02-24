# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from orchestrator.workflows import LazyWorkflowInstance

LazyWorkflowInstance("workflows.tasks.bulk_create_optical_devices", "bulk_create_optical_devices")
LazyWorkflowInstance("workflows.tasks.bulk_create_optical_fibers", "bulk_create_optical_fibers")
LazyWorkflowInstance("workflows.tasks.check_netbox_connection", "task_check_netbox_connection")
LazyWorkflowInstance("workflows.tasks.import_fibers_from_tnms", "import_fibers_from_tnms")
LazyWorkflowInstance("workflows.tasks.import_pops_from_netbox", "import_pops_from_netbox")
LazyWorkflowInstance("workflows.tasks.purge_subscription_from_database", "purge_subscription_from_database")
LazyWorkflowInstance("workflows.tasks.task_check_tnms_connection", "task_check_tnms_connection")
LazyWorkflowInstance("workflows.tasks.bulk_validate_optical_fibers", "bulk_validate_optical_fibers")
LazyWorkflowInstance("workflows.tasks.execute_tl1_commands_on_flexils", "execute_tl1_commands_on_flexils")
LazyWorkflowInstance("workflows.tasks.upgrade_g30_from_452_to_480", "upgrade_g30_from_452_to_480")
LazyWorkflowInstance("workflows.tasks.upgrade_g42_from_600_to_802", "upgrade_g42_from_600_to_802")

LazyWorkflowInstance("workflows.optical_device.create_optical_device", "create_optical_device")
LazyWorkflowInstance("workflows.optical_device.modify_optical_device", "modify_optical_device")
LazyWorkflowInstance("workflows.optical_device.terminate_optical_device", "terminate_optical_device")
LazyWorkflowInstance("workflows.optical_device.validate_optical_device", "validate_optical_device")

LazyWorkflowInstance("workflows.optical_fiber.create_optical_fiber", "create_optical_fiber")
LazyWorkflowInstance("workflows.optical_fiber.modify_optical_fiber", "modify_optical_fiber")
LazyWorkflowInstance("workflows.optical_fiber.terminate_optical_fiber", "terminate_optical_fiber")
LazyWorkflowInstance("workflows.optical_fiber.validate_optical_fiber", "validate_optical_fiber")

LazyWorkflowInstance("workflows.optical_spectrum.create_optical_spectrum", "create_optical_spectrum")
LazyWorkflowInstance("workflows.optical_spectrum.modify_optical_spectrum", "modify_optical_spectrum")
LazyWorkflowInstance("workflows.optical_spectrum.terminate_optical_spectrum", "terminate_optical_spectrum")
LazyWorkflowInstance("workflows.optical_spectrum.validate_optical_spectrum", "validate_optical_spectrum")

LazyWorkflowInstance(
    "workflows.optical_digital_service.create_optical_digital_service", "create_optical_digital_service"
)
LazyWorkflowInstance(
    "workflows.optical_digital_service.modify_optical_digital_service", "modify_optical_digital_service"
)
LazyWorkflowInstance(
    "workflows.optical_digital_service.terminate_optical_digital_service", "terminate_optical_digital_service"
)
LazyWorkflowInstance(
    "workflows.optical_digital_service.validate_optical_digital_service", "validate_optical_digital_service"
)
