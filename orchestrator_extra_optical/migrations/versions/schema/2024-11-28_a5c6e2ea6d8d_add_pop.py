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

"""Add pop product.

Revision ID: a5c6e2ea6d8d
Revises:
Create Date: 2024-11-28 18:57:53.321893

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
revision = "a5c6e2ea6d8d"
down_revision = None
branch_labels = ("data",)
depends_on = "da5c9f4cce1c"

new_products = {
    "products": {
        "pop": {
            "product_id": uuid4(),
            "product_type": "PoP",
            "description": "Product of a Point of Presence",
            "tag": "POP",
            "status": "active",
            "root_product_block": "PoP",
            "fixed_inputs": {},
        },
    },
    "product_blocks": {
        "PoP": {
            "product_block_id": uuid4(),
            "description": "Product Block of a Point of Presence",
            "tag": "POP",
            "status": "active",
            "resources": {
                "garrxdb_id": "ID of the Point of Presence in GARRXDB",
                "netbox_id": "ID of the Point of Presence in NetBox",
                "code": "Unique code of the Point of Presence, e.g. AZ99",
                "full_name": "Full name of the Point of Presence",
                "latitude": "Latitude of the Point of Presence",
                "longitude": "Longitude of the Point of Presence",
            },
            "depends_on_block_relations": [],
        },
    },
    "workflows": {},
}

new_workflows = [
    {
        "name": "create_pop",
        "target": Target.CREATE,
        "description": "create Point of Presence",
        "product_type": "PoP",
    },
    {
        "name": "modify_pop",
        "target": Target.MODIFY,
        "description": "modify Point of Presence",
        "product_type": "PoP",
    },
    {
        "name": "terminate_pop",
        "target": Target.TERMINATE,
        "description": "terminate Point of Presence",
        "product_type": "PoP",
    },
    {
        "name": "validate_pop",
        "target": Target.SYSTEM,
        "description": "validate Point of Presence",
        "product_type": "PoP",
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
