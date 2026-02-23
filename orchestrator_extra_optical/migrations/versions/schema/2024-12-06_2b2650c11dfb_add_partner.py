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

"""Add partner product.

Revision ID: 2b2650c11dfb
Revises: d946c20663d3
Create Date: 2024-12-06 16:25:03.741954

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
revision = "2b2650c11dfb"
down_revision = "d946c20663d3"
branch_labels = None
depends_on = None

new_products = {
    "products": {
        "partner": {
            "product_id": uuid4(),
            "product_type": "Partner",
            "description": "Product of a Partner",
            "tag": "PARTNER",
            "status": "active",
            "root_product_block": "Partner",
            "fixed_inputs": {},
        },
    },
    "product_blocks": {
        "Partner": {
            "product_block_id": uuid4(),
            "description": "Product Block of a Partner",
            "tag": "PARTNER",
            "status": "active",
            "resources": {
                "garrxdb_id": "ID of the Partner in GARRXDB",
                "netbox_id": "ID of the Partner in NetBox",
                "partner_name": "Name of the Partner",
                "partner_type": "Type of the Partner",
            },
            "depends_on_block_relations": [],
        },
    },
    "workflows": {},
}

new_workflows = [
    {
        "name": "create_partner",
        "target": Target.CREATE,
        "description": "create Partner",
        "product_type": "Partner",
    },
    {
        "name": "modify_partner",
        "target": Target.MODIFY,
        "description": "modify Partner",
        "product_type": "Partner",
    },
    {
        "name": "terminate_partner",
        "target": Target.TERMINATE,
        "description": "terminate Partner",
        "product_type": "Partner",
    },
    {
        "name": "validate_partner",
        "target": Target.SYSTEM,
        "description": "validate Partner",
        "product_type": "Partner",
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
