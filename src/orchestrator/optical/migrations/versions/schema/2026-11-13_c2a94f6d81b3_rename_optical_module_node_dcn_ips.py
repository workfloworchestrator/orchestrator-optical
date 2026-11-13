"""rename optical module node dcn ips to management ips

Renames the ``optical_module_node_dcn_interface_ip`` and
``optical_module_node_dcn_loopback_ip`` resource types of the Optical Module Node
Management block to ``optical_module_node_management_ip`` and
``optical_module_node_management_loopback_ip``. "DCN" is vendor wording: the two
addresses are simply how the node is reached, whatever the management network is called.

The resource type rows are renamed in place, so their links to the product blocks and
the values stored on the subscription instances are kept as they are (every stored value
is a plain IP address, valid under either name).

The downgrade renames them back; nothing else changes.

Revision ID: c2a94f6d81b3
Revises: 8e2f4a6c1d93
Create Date: 2026-11-13

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c2a94f6d81b3"
down_revision = "8e2f4a6c1d93"
branch_labels = None
depends_on = None

#: ``(resource type, description)`` pairs, old name first.
RENAMES = (
    (
        ("optical_module_node_dcn_loopback_ip", "Optical Module Node Dcn Loopback Ip"),
        ("optical_module_node_management_loopback_ip", "Optical Module Node Management Loopback Ip"),
    ),
    (
        ("optical_module_node_dcn_interface_ip", "Optical Module Node Dcn Interface Ip"),
        ("optical_module_node_management_ip", "Optical Module Node Management Ip"),
    ),
)

RENAME = sa.text(
    """UPDATE resource_types
       SET resource_type = :new_name,
           description   = :new_description
       WHERE resource_type = :old_name"""
)


def _rename(renames: tuple[tuple[tuple[str, str], tuple[str, str]], ...]) -> None:
    """Rename each resource type, with its description, in place."""
    conn = op.get_bind()
    for old, new in renames:
        conn.execute(RENAME, {"old_name": old[0], "new_name": new[0], "new_description": new[1]})


def upgrade() -> None:
    _rename(RENAMES)


def downgrade() -> None:
    _rename(tuple((new, old) for old, new in RENAMES))
