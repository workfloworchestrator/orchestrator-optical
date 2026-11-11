"""Database tests of the ``optical_applied_config`` table and its query helpers."""

from uuid import uuid4

import pytest
from sqlalchemy import inspect as sa_inspect

import orchestrator.core.db as core_db
from orchestrator.optical import db as optical_db
from orchestrator.optical.db import OpticalAppliedConfigTable
from test.support.db import node_instance_id_of_subscription

pytestmark = pytest.mark.db

GROOVE_G30_PRODUCT = "Nokia Groove G30 Optical Node"
PORT = "/ne:ne/shelf[shelf-id='1']/slot[slot-id='2']/card/port[port-id='1']"


@pytest.fixture
def node_id(seed_optical_node) -> str:
    subscription_id = seed_optical_node(GROOVE_G30_PRODUCT, "g30-config-01.optical.test", "192.0.2.61")
    return node_instance_id_of_subscription(subscription_id)


def test_shipped_revision_creates_the_table_of_the_model(postgres_database) -> None:
    """The table created by the shipped Alembic revision has the columns and key of the model."""
    inspector = sa_inspect(core_db.db.engine)
    table = OpticalAppliedConfigTable.__table__

    columns = {column["name"]: column["nullable"] for column in inspector.get_columns(table.name)}
    assert columns == {column.name: column.nullable for column in table.columns}
    assert inspector.get_pk_constraint(table.name)["constrained_columns"] == [c.name for c in table.primary_key]
    assert [index["column_names"] for index in inspector.get_indexes(table.name)] == [["owner_instance_id"]]


def test_applied_config_is_recorded_per_owner_and_scope(node_id: str) -> None:
    owner, other = uuid4(), uuid4()
    with core_db.db.database_scope():
        optical_db.lock_node_config(node_id)
        optical_db.replace_applied_config(node_id, owner, "line", {f"{PORT}/admin-status": "up", f"{PORT}/x": 1})
        optical_db.replace_applied_config(node_id, owner, "client:p", {f"{PORT}/label": "svc"})
        optical_db.replace_applied_config(node_id, other, "termination", {f"{PORT}/admin-status": "up"})

        assert optical_db.applied_config(node_id, owner, "line") == {f"{PORT}/admin-status": "up", f"{PORT}/x": 1}
        assert optical_db.applied_config_of_other_owners(node_id, owner) == {f"{PORT}/admin-status": "up"}
        assert optical_db.node_applied_config(node_id) == {
            f"{PORT}/admin-status": "up",
            f"{PORT}/label": "svc",
            f"{PORT}/x": 1,
        }


def test_replacing_a_scope_drops_what_it_no_longer_holds_and_keeps_the_other_scopes(node_id: str) -> None:
    owner = uuid4()
    with core_db.db.database_scope():
        optical_db.replace_applied_config(node_id, owner, "line", {f"{PORT}/a": "1", f"{PORT}/b": "2"})
        optical_db.replace_applied_config(node_id, owner, "client:p", {f"{PORT}/c": "3"})

        optical_db.replace_applied_config(node_id, owner, "line", {f"{PORT}/b": "20"})

        assert optical_db.applied_config(node_id, owner, "line") == {f"{PORT}/b": "20"}
        assert optical_db.applied_config(node_id, owner, "client:p") == {f"{PORT}/c": "3"}

        optical_db.forget_applied_config(node_id, owner, "line")

        assert optical_db.applied_config(node_id, owner, "line") == {}
        assert optical_db.node_applied_config(node_id) == {f"{PORT}/c": "3"}


def test_a_path_an_owner_already_holds_moves_to_the_scope_that_applies_it_again(node_id: str) -> None:
    owner = uuid4()
    with core_db.db.database_scope():
        optical_db.replace_applied_config(node_id, owner, "termination", {f"{PORT}/admin-status": "up"})
        optical_db.replace_applied_config(node_id, owner, "admin-state", {f"{PORT}/admin-status": "down"})

        assert optical_db.applied_config(node_id, owner, "termination") == {}
        assert optical_db.applied_config(node_id, owner, "admin-state") == {f"{PORT}/admin-status": "down"}
