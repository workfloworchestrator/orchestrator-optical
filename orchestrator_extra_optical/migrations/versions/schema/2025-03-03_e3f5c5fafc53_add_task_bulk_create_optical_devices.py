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

"""add task to bulk create optical devices

Revision ID: e3f5c5fafc53
Revises: ba0d8bb080ab
Create Date: 2025-03-03 18:21:00.000000

"""

import sqlalchemy as sa
from alembic import op
from orchestrator.migrations.helpers import delete_workflow
from orchestrator.targets import Target

# revision identifiers, used by Alembic.
revision = "e3f5c5fafc53"
down_revision = "ba0d8bb080ab"
branch_labels = None
depends_on = None

tasks = [
    {
        "name": "bulk_create_optical_devices",
        "target": Target.SYSTEM,
        "description": "Create optical devices in bulk from CSV data",
    },
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
