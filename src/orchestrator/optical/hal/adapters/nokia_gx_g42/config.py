"""Nokia GX G42 side of the declarative configuration: the client and the release rule.

See :mod:`orchestrator.optical.hal.reconcile`. The rule says how a path this module
applied is taken off a GX G42 once no product block renders it any more.
"""

from typing import Final

from orchestrator.optical.hal.adapters.nokia_gx_g42._shared import get_g42_client
from orchestrator.optical.hal.reconcile import DeleteEntry, Reset, leaf_name, parent_name, split_instance_path

__all__ = ["get_g42_client", "release_rule"]

#: Factory value of the leaves of the GX G42 objects that outlive a service.
_RESETS: Final[dict[str, str]] = {
    "admin-state": "lock",
    "label": "",
    "connected-to": "",
    "external-connectivity": "no",
}

#: The objects whose leaves are reset: they exist whether a service uses them or not.
_RESET_PARENTS: Final = frozenset({"port", "tom", "trib-ptp", "ethernet", "super-channel-group"})

#: The list entries created for a service, deleted with it.
_DELETED_ENTRIES: Final = ("xcon[", "super-channel[")


def release_rule(path: str) -> Reset | DeleteEntry | None:
    """Return how a released path is taken off a GX G42.

    - A cross-connect and a super-channel are list entries created for a service: they
      are deleted.
    - The leaves of a port, its TOM, its tributary, its ethernet facility and its
      super-channel group go back to their factory value.
    - Everything else is left alone: the optical carriers go with their super-channel.
    """
    segments = split_instance_path(path)
    for index, segment in enumerate(segments):
        if segment.startswith(_DELETED_ENTRIES):
            return DeleteEntry("/" + "/".join(segments[: index + 1]))
    if parent_name(path) not in _RESET_PARENTS:
        return None
    leaf = leaf_name(path)
    return Reset(_RESETS[leaf]) if leaf in _RESETS else None
