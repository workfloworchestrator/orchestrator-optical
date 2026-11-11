"""optical applied config

Creates the ``optical_applied_config`` table: the device configuration applied by the
module, one row per (node, path, owner); see ``orchestrator.optical.db`` and
``orchestrator.optical.hal.reconcile``.

The revision is independent of the catalog baseline (a table, not catalog rows): it
branches off the pinned orchestrator-core schema revision under its own branch label, so
it can be applied on its own with ``upgrade optical_applied_config@head``.

Revision ID: 7c1d5e9a4b20
Revises: ca79fd834ba0
Create Date: 2026-11-10

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = "7c1d5e9a4b20"
down_revision = "ca79fd834ba0"
branch_labels = ("optical_applied_config",)
depends_on = None

TABLE = "optical_applied_config"


def upgrade() -> None:
    op.create_table(
        TABLE,
        sa.Column(
            "node_instance_id",
            UUIDType(),
            sa.ForeignKey("subscription_instances.subscription_instance_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("owner_instance_id", UUIDType(), nullable=False),
        sa.Column("scope", sa.String(255), nullable=False),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column(
            "applied_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("current_timestamp"), nullable=False
        ),
        sa.PrimaryKeyConstraint("node_instance_id", "path", "owner_instance_id"),
    )
    op.create_index(f"ix_{TABLE}_owner_instance_id", TABLE, ["owner_instance_id"])


def downgrade() -> None:
    op.drop_index(f"ix_{TABLE}_owner_instance_id", table_name=TABLE)
    op.drop_table(TABLE)
