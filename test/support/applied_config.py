"""An in-memory stand-in for the ``optical_applied_config`` table.

``applied_config_store`` replaces the query helpers of :mod:`orchestrator.optical.db` that
:mod:`orchestrator.optical.hal.reconcile` uses, so the declarative configuration runs in
the database-free lane. The store keeps one ``(scope, value)`` per ``(node, path, owner)``,
like the table.
"""

from typing import Any
from uuid import UUID

import pytest

from orchestrator.optical import db as optical_db


class AppliedConfigStore:
    """Rows of the applied configuration, keyed by ``(node, path, owner)``."""

    def __init__(self) -> None:
        self.rows: dict[tuple[UUID, str, UUID], tuple[str, Any]] = {}
        self.locked: list[UUID] = []

    def lock_node_config(self, node_instance_id: Any) -> None:
        self.locked.append(UUID(str(node_instance_id)))

    def applied_config(self, node_instance_id: Any, owner_instance_id: Any, scope: str) -> dict[str, Any]:
        node, owner = UUID(str(node_instance_id)), UUID(str(owner_instance_id))
        return {
            path: value
            for (row_node, path, row_owner), (row_scope, value) in self.rows.items()
            if (row_node, row_owner, row_scope) == (node, owner, scope)
        }

    def applied_config_of_other_owners(self, node_instance_id: Any, owner_instance_id: Any) -> dict[str, Any]:
        node, owner = UUID(str(node_instance_id)), UUID(str(owner_instance_id))
        return {
            path: value
            for (row_node, path, row_owner), (_, value) in self.rows.items()
            if row_node == node and row_owner != owner
        }

    def node_applied_config(self, node_instance_id: Any) -> dict[str, Any]:
        node = UUID(str(node_instance_id))
        return {path: value for (row_node, path, _), (_, value) in sorted(self.rows.items()) if row_node == node}

    def replace_applied_config(
        self, node_instance_id: Any, owner_instance_id: Any, scope: str, config: dict[str, Any]
    ) -> None:
        node, owner = UUID(str(node_instance_id)), UUID(str(owner_instance_id))
        for key in [
            key for key, (row_scope, _) in self.rows.items() if (key[0], key[2], row_scope) == (node, owner, scope)
        ]:
            del self.rows[key]
        for path, value in config.items():
            self.rows[(node, path, owner)] = (scope, value)

    def forget_applied_config(self, node_instance_id: Any, owner_instance_id: Any, scope: str) -> None:
        self.replace_applied_config(node_instance_id, owner_instance_id, scope, {})


@pytest.fixture
def applied_config_store(monkeypatch: pytest.MonkeyPatch) -> AppliedConfigStore:
    """Back the applied-configuration helpers of ``orchestrator.optical.db`` with an in-memory store."""
    store = AppliedConfigStore()
    for name in (
        "lock_node_config",
        "applied_config",
        "applied_config_of_other_owners",
        "node_applied_config",
        "replace_applied_config",
        "forget_applied_config",
    ):
        monkeypatch.setattr(optical_db, name, getattr(store, name))
    return store
