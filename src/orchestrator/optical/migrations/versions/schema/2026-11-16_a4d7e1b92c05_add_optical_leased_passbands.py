"""add optical leased passbands

Adds the ``optical_leased_passbands`` resource type to the Leased Spectrum block: the
frequency ranges leased on the pipe, outside of which nothing may be transmitted.

Existing Leased Spectrum subscriptions get no value: an empty list means the lease is
not restricted, which is how they behaved so far. Set the passbands with the modify
workflow.

The downgrade removes the resource type together with the values stored for it.

Revision ID: a4d7e1b92c05
Revises: c2a94f6d81b3
Create Date: 2026-11-16

"""

import sqlalchemy as sa
from alembic import op

from orchestrator.core.migrations.helpers import (
    create_resource_types_for_product_blocks,
    delete_resource_types_from_product_blocks,
)

# revision identifiers, used by Alembic.
revision = "a4d7e1b92c05"
down_revision = "c2a94f6d81b3"
branch_labels = None
depends_on = None

RESOURCE_TYPE = "optical_leased_passbands"
NEW_RESOURCE_TYPES = {"LeasedSpectrumBlock": {RESOURCE_TYPE: "Optical Leased Passbands"}}


def upgrade() -> None:
    create_resource_types_for_product_blocks(op.get_bind(), NEW_RESOURCE_TYPES)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """DELETE
               FROM subscription_instance_values AS siv
                   USING resource_types AS rt
               WHERE siv.resource_type_id = rt.resource_type_id
                 AND rt.resource_type = :resource_type"""
        ),
        {"resource_type": RESOURCE_TYPE},
    )
    delete_resource_types_from_product_blocks(conn, NEW_RESOURCE_TYPES)
    conn.execute(
        sa.text("DELETE FROM resource_types WHERE resource_type = :resource_type"), {"resource_type": RESOURCE_TYPE}
    )
