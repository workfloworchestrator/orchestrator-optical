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

"""add task to update the passbands of optical fibers.

Revision ID: f001ccbe103c
Revises: 5e527c2f8e75
Create Date: 2025-07-08 11:10:00.000000

"""

import sqlalchemy as sa
from alembic import op
from orchestrator.migrations.helpers import delete_workflow
from orchestrator.targets import Target

# revision identifiers, used by Alembic.
revision = "f001ccbe103c"
down_revision = "5e527c2f8e75"
branch_labels = None
depends_on = None

tasks = [
    {
        "name": "bulk_validate_optical_fibers",
        "target": Target.SYSTEM,
        "description": "Update passbands (validate) of Optical Fibers attached to a list of ROADMs",
    }
]


def upgrade() -> None:
    conn = op.get_bind()
    for task in tasks:
        conn.execute(
            sa.text(
                """INSERT INTO workflows(name, target, description) VALUES (:name, :target, :description)
                   ON CONFLICT DO NOTHING"""
            ),
            task,
        )


def downgrade() -> None:
    conn = op.get_bind()
    for task in tasks:
        delete_workflow(conn, task["name"])
