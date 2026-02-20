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

"""add task to upgrade G42 devices from FP6.0.0 to FP8.0.2.

Revision ID: d0cd928e361f
Revises: e3d84c9722c1
Create Date: 2025-12-03 17:44:00.000000

"""

import sqlalchemy as sa
from alembic import op
from orchestrator.migrations.helpers import delete_workflow
from orchestrator.targets import Target

# revision identifiers, used by Alembic.
revision = "d0cd928e361f"
down_revision = "e3d84c9722c1"
branch_labels = None
depends_on = None

tasks = [
    {
        "name": "upgrade_g42_from_600_to_802",
        "target": Target.SYSTEM,
        "description": "Task to upgrade G42 devices from FP6.0.0 to FP8.0.2",
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
