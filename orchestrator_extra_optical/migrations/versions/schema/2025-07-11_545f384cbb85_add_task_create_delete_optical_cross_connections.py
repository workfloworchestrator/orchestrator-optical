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

Revision ID: 545f384cbb85
Revises: f001ccbe103c
Create Date: 2025-07-11 10:10:00.000000

"""

import sqlalchemy as sa
from alembic import op
from orchestrator.migrations.helpers import delete_workflow
from orchestrator.targets import Target

# revision identifiers, used by Alembic.
revision = "545f384cbb85"
down_revision = "f001ccbe103c"
branch_labels = None
depends_on = None

tasks = [
    {
        "name": "create_delete_optical_cross_connections",
        "target": Target.SYSTEM,
        "description": "Task to create or delete optical cross connections on a ROADM degree",
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
