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

"""Add optical_device product.

Revision ID: b0ecb1a9b6d0
Revises: a5c6e2ea6d8d
Create Date: 2024-11-28 19:12:50.072516

"""

from uuid import uuid4

from alembic import op
from orchestrator.migrations.helpers import (
    create,
    create_workflow,
    delete,
    delete_workflow,
    ensure_default_workflows,
)
from orchestrator.targets import Target

# revision identifiers, used by Alembic.
revision = "b0ecb1a9b6d0"
down_revision = "a5c6e2ea6d8d"
branch_labels = None
depends_on = None

new_products = {
    "products": {
        "optical_device": {
            "product_id": uuid4(),
            "product_type": "OpticalDevice",
            "description": "Product of an Optical Device with an operating system and a management interface, e.g. ROADM, ILA, G30 (H4), pluggable coherent",
            "tag": "OPTICAL_DEVICE",
            "status": "active",
            "root_product_block": "OpticalDevice",
            "fixed_inputs": {},
        },
    },
    "product_blocks": {
        "OpticalDevice": {
            "product_block_id": uuid4(),
            "description": "Product Block of an Optical Device with an operating system and a management interface, e.g. ROADM, ILA, G30 (H4), pluggable coherent",
            "tag": "OPTICAL_DEVICE",
            "status": "active",
            "resources": {
                "fqdn": "The device FQDN, e.g. flex.pop.garr.net, g30.pop.garr.net, g42.pop.garr.net",
                "vendor": "The device vendor",
                "platform": "The device platform or family (same operating system)",
                "device_type": "The device type",
                "lo_ip": "The device loopback IP address",
                "mngmt_ip": "The device management IP address",
                "nms_uuid": "Identifier of the device in its Network Management System (NMS)",
                "netbox_id": "Identifier of this device in NetBox",
            },
            "depends_on_block_relations": [
                "PoP",
            ],
        },
    },
    "workflows": {},
}

new_workflows = [
    {
        "name": "create_optical_device",
        "target": Target.CREATE,
        "description": "create optical device",
        "product_type": "OpticalDevice",
    },
    {
        "name": "modify_optical_device",
        "target": Target.MODIFY,
        "description": "modify optical device",
        "product_type": "OpticalDevice",
    },
    {
        "name": "terminate_optical_device",
        "target": Target.TERMINATE,
        "description": "terminate optical device",
        "product_type": "OpticalDevice",
    },
    {
        "name": "validate_optical_device",
        "target": Target.SYSTEM,
        "description": "validate optical device",
        "product_type": "OpticalDevice",
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    create(conn, new_products)
    for workflow in new_workflows:
        create_workflow(conn, workflow)
    ensure_default_workflows(conn)


def downgrade() -> None:
    conn = op.get_bind()
    for workflow in new_workflows:
        delete_workflow(conn, workflow["name"])

    delete(conn, new_products)
