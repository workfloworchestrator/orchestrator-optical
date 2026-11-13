"""Nokia Groove G30 side of the declarative configuration: the client and the release rule.

See :mod:`orchestrator.optical.hal.reconcile`. The rule says how a path this module
applied is taken off a Groove G30 once no product block renders it any more.
"""

from typing import Final

from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import get_g30_client
from orchestrator.optical.hal.reconcile import DeleteEntry, Reset, leaf_name, parent_name, split_instance_path

__all__ = ["get_g30_client", "release_rule"]

#: Factory value of the leaves of a Groove G30 port or subport.
_PORT_RESETS: Final[dict[str, str]] = {
    "admin-status": "down",
    "service-label": "",
    "connected-to": "",
    "external-connectivity": "no",
    "port-mode": "not-applicable",
}


def release_rule(path: str) -> Reset | DeleteEntry | None:
    """Return how a released path is taken off a Groove G30.

    - A cross-connect is a list entry created by the orchestrator: it is deleted.
    - The leaves of a port or subport go back to their factory value. On a port of an
      ``OCC2`` subcard only the ``connected-to`` and ``service-label`` notes are cleared:
      the Open Line System ports stay in service.
    - Everything else is left alone: the optical channel and the ethernet facility of a
      port are removed by the device when the port mode is reset, and the amplifiers
      keep their settings.
    """
    segments = split_instance_path(path)
    for index, segment in enumerate(segments):
        if segment.startswith("CRS["):
            return DeleteEntry("/" + "/".join(segments[: index + 1]))
    if parent_name(path) not in {"port", "subport"}:
        return None
    leaf = leaf_name(path)
    if any(segment.startswith("subslot[") for segment in segments) and leaf not in {"connected-to", "service-label"}:
        return None
    return Reset(_PORT_RESETS[leaf]) if leaf in _PORT_RESETS else None
