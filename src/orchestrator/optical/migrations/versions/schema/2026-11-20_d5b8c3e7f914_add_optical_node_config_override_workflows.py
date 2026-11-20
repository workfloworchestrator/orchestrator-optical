"""add optical node config override workflows

Adds the ``modify_optical_node_nokia_groove_g30_config_override`` and
``modify_optical_node_nokia_gx_g42_config_override`` workflows: the NOC changes the
configuration of a Groove G30 or GX G42 by hand, the overrides being recorded in
``optical_applied_config`` under the ``override`` scope of the node block.

Revision ID: d5b8c3e7f914
Revises: a4d7e1b92c05
Create Date: 2026-11-20

"""

from alembic import op

from orchestrator.core.migrations.helpers import create_workflow, delete_workflow

# revision identifiers, used by Alembic.
revision = "d5b8c3e7f914"
down_revision = "a4d7e1b92c05"
branch_labels = None
depends_on = None

new_workflows = [
    {
        "name": "modify_optical_node_nokia_groove_g30_config_override",
        "target": "MODIFY",
        "description": "override configuration of Nokia Groove G30 optical node",
        "product_type": "OpticalNodeNokiaGrooveG30Subscription",
    },
    {
        "name": "modify_optical_node_nokia_gx_g42_config_override",
        "target": "MODIFY",
        "description": "override configuration of Nokia GX G42 optical node",
        "product_type": "OpticalNodeNokiaGxG42Subscription",
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    for workflow in new_workflows:
        create_workflow(conn, workflow)


def downgrade() -> None:
    conn = op.get_bind()
    for workflow in new_workflows:
        delete_workflow(conn, workflow["name"])
