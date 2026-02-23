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

"""add task to upgrade G30 devices from FP4.5.2 to FP4.8.0.

Revision ID: e3d84c9722c1
Revises: 43ec72c4b513
Create Date: 2025-10-23 10:10:00.000000

"""

import sqlalchemy as sa
from alembic import op
from orchestrator.migrations.helpers import delete_workflow
from orchestrator.targets import Target

# revision identifiers, used by Alembic.
revision = "e3d84c9722c1"
down_revision = "43ec72c4b513"
branch_labels = None
depends_on = None

tasks = [
    {
        "name": "upgrade_g30_from_452_to_480",
        "target": Target.SYSTEM,
        "description": "Task to upgrade G30 devices from FP4.5.2 to FP4.8.0",
        "is_task": True,
    }
]


def upgrade() -> None:
    conn = op.get_bind()
    for task in tasks:
        conn.execute(
            sa.text(
                """INSERT INTO workflows(name, target, description,is_task) VALUES (:name, :target, :description, :is_task)
                   ON CONFLICT DO NOTHING"""
            ),
            task,
        )


def downgrade() -> None:
    conn = op.get_bind()
    for task in tasks:
        delete_workflow(conn, task["name"])
