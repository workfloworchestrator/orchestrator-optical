"""Unit tests for the FlexILS OEL deletion guard (database-free).

The OEL explicit route cannot be edited with ED-OEL, so a path change is applied by
deleting the OEL and re-entering it. Before deleting an OEL the node must be checked
with RTRV-OSNC: this module covers that guard.
"""

from typing import Any

from orchestrator.optical.hal.adapters.nokia_flexils.spectrum import _delete_oel_if_unused


class _FakeFlex:
    """Fake TL1 client exposing just the commands used by the OEL deletion guard."""

    def __init__(self, osnc_records: list[dict[str, Any]]) -> None:
        self.osnc_records = osnc_records
        self.deleted_oels: list[str] = []

    def rtrv_osnc(self) -> Any:
        return type("_Response", (), {"parsed_data": self.osnc_records})()

    def dlt_oel(self, aid: str) -> Any:
        self.deleted_oels.append(aid)
        return None


def test_delete_oel_if_unused_deletes_when_no_osnc_references_it() -> None:
    flex = _FakeFlex([{"OELAID": "other-oel", "LOCENDPOINT": "1-A-1-L1-1"}])

    _delete_oel_if_unused(flex, "my-oel")

    assert flex.deleted_oels == ["my-oel"]


def test_delete_oel_if_unused_leaves_oel_when_another_osnc_references_it() -> None:
    flex = _FakeFlex([{"OELAID": "my-oel", "LOCENDPOINT": "1-A-1-L1-1"}])

    _delete_oel_if_unused(flex, "my-oel")

    assert flex.deleted_oels == []
