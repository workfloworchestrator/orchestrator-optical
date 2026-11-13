"""rename optical module node fqdn to name

Renames the ``optical_module_node_fqdn`` resource type of the Optical Module Node
Management block to ``optical_module_node_name``. The field no longer has to be a fully
qualified domain name: it is the name the node is known by, by default the one read from
the device when the node is created, and it was never used to reach the node.

The resource type row is renamed in place, so its links to the product blocks and the
values stored on the subscription instances are kept as they are (every stored FQDN is a
valid name).

The downgrade renames it back; a name stored meanwhile that is not a fully qualified
domain name then fails the validation of the previous model when its subscription is loaded.

Revision ID: 8e2f4a6c1d93
Revises: 53ca2ddbe138
Create Date: 2026-11-13

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8e2f4a6c1d93"
down_revision = "53ca2ddbe138"
branch_labels = None
depends_on = None

OLD = ("optical_module_node_fqdn", "Optical Module Node Fqdn")
NEW = ("optical_module_node_name", "Optical Module Node Name")

RENAME = sa.text(
    """UPDATE resource_types
       SET resource_type = :new_name,
           description   = :new_description
       WHERE resource_type = :old_name"""
)


def _rename(old: tuple[str, str], new: tuple[str, str]) -> None:
    op.get_bind().execute(RENAME, {"old_name": old[0], "new_name": new[0], "new_description": new[1]})


def upgrade() -> None:
    _rename(OLD, NEW)


def downgrade() -> None:
    _rename(NEW, OLD)
