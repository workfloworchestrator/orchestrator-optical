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

"""add Netbox health check task.

Revision ID: 57fbb3cbadfb
Revises: 2b2650c11dfb
Create Date: 2025-01-27 15:52:00.000000


NOTA: le migrazioni per i task vanno create a mano.
    Non ho trovato alcun comando che le generi sulla base del codice (come per le migrazioni),
    sulla doc ufficiale non c'e' alcuna specifica a riguardo al momento.

"""

import sqlalchemy as sa
from alembic import op
from orchestrator.migrations.helpers import delete_workflow
from orchestrator.targets import Target

# revision identifiers, used by Alembic.
revision = "57fbb3cbadfb"
down_revision = "2b2650c11dfb"
branch_labels = None
depends_on = None

tasks = [
    {
        "name": "task_check_netbox_connection",
        "target": Target.SYSTEM,
        "description": "Check Netbox connection",
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
