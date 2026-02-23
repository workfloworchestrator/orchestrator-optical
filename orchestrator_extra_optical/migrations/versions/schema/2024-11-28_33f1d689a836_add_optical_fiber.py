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

"""Add optical_fiber product.

Revision ID: 33f1d689a836
Revises: b0ecb1a9b6d0
Create Date: 2024-11-28 19:19:08.559235

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
revision = "33f1d689a836"
down_revision = "b0ecb1a9b6d0"
branch_labels = None
depends_on = None

new_products = {
    "products": {
        "optical_fiber": {
            "product_id": uuid4(),
            "product_type": "OpticalFiber",
            "description": "product of an optical fiber between two optical ports",
            "tag": "OPTICAL_FIBER",
            "status": "active",
            "root_product_block": "OpticalFiber",
            "fixed_inputs": {},
        },
    },
    "product_blocks": {
        "OpticalDevicePort": {
            "product_block_id": uuid4(),
            "description": "product block of a port on an optical device",
            "tag": "OPTICAL_DEVICE_PORT",
            "status": "active",
            "resources": {
                "port_name": "the port identifier in the hosting device",
                "port_description": "the port description",
                "netbox_id": "Identifier of this port in NetBox",
                "used_passbands": "the list of passbands ([int, int] in MHz) that are in use on this fiber",
            },
            "depends_on_block_relations": [
                "OpticalDevice",
            ],
        },
        "OpticalFiber": {
            "product_block_id": uuid4(),
            "description": "product block of an optical fiber between two optical ports",
            "tag": "OPTICAL_FIBER",
            "status": "active",
            "resources": {
                "fiber_name": "the optical fiber human-friendly name",
                "garrxdb_id": "the optical fiber identifier in GARRXDB",
                "lengths": "the ordered list of lengths (int in meters) of the fiber segments",
                "fiber_types": "the ordered sequence of fiber types of the fiber segments making up the complete fiber",
                "total_loss": "the total loss (float in dB) of the fiber, including all splices, connectors, and fixed attenuators",
            },
            "depends_on_block_relations": [
                "OpticalDevicePort",
            ],
        },
    },
    "workflows": {},
}

new_workflows = [
    {
        "name": "create_optical_fiber",
        "target": Target.CREATE,
        "description": "create optical fiber",
        "product_type": "OpticalFiber",
    },
    {
        "name": "modify_optical_fiber",
        "target": Target.MODIFY,
        "description": "modify optical fiber",
        "product_type": "OpticalFiber",
    },
    {
        "name": "terminate_optical_fiber",
        "target": Target.TERMINATE,
        "description": "terminate optical fiber",
        "product_type": "OpticalFiber",
    },
    {
        "name": "validate_optical_fiber",
        "target": Target.SYSTEM,
        "description": "validate optical fiber",
        "product_type": "OpticalFiber",
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
