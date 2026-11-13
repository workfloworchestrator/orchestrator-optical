"""drop optical port description

Removes the ``optical_port_description`` resource type from the four Optical Port blocks
(OLS add/drop, OLS line, transponder client, transponder line) together with the values
stored for it on their subscription instances. The label written on a device is now
computed from the owner (pipe, spectrum, digital service) each time it is written or
checked (``orchestrator.optical.utils.labels``), so the stored copy only went stale.

The resource type itself stays: the Coherent Pluggable block keeps it as a user-entered
description.

The downgrade links the resource type back to the four blocks; the removed values are not
restored (they load as ``None``, and the labels on the devices are untouched).

Revision ID: 53ca2ddbe138
Revises: 3b3fe1c2a7a6
Create Date: 2026-11-13

"""

import sqlalchemy as sa
from alembic import op

from orchestrator.core.migrations.helpers import (
    create_resource_types_for_product_blocks,
    delete_resource_types_from_product_blocks,
)

# revision identifiers, used by Alembic.
revision = "53ca2ddbe138"
down_revision = "3b3fe1c2a7a6"
branch_labels = None
depends_on = None

RESOURCE_TYPE = "optical_port_description"
RESOURCE_TYPE_DESCRIPTION = "Optical Port Description"
PORT_BLOCKS = (
    "OlsAddDropPortBlock",
    "OlsLinePortBlock",
    "OpticalTransponderClientPortBlock",
    "OpticalTransponderLinePortBlock",
)


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """DELETE
               FROM subscription_instance_values AS siv
                   USING subscription_instances AS si, product_blocks AS pb, resource_types AS rt
               WHERE siv.subscription_instance_id = si.subscription_instance_id
                 AND si.product_block_id = pb.product_block_id
                 AND siv.resource_type_id = rt.resource_type_id
                 AND rt.resource_type = :resource_type
                 AND pb.name = ANY (:product_blocks)"""
        ),
        {"resource_type": RESOURCE_TYPE, "product_blocks": list(PORT_BLOCKS)},
    )
    delete_resource_types_from_product_blocks(
        conn, {block: {RESOURCE_TYPE: RESOURCE_TYPE_DESCRIPTION} for block in PORT_BLOCKS}
    )


def downgrade() -> None:
    conn = op.get_bind()
    create_resource_types_for_product_blocks(
        conn, {block: {RESOURCE_TYPE: RESOURCE_TYPE_DESCRIPTION} for block in PORT_BLOCKS}
    )
