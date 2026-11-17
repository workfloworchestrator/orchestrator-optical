"""Naming rules of the labels written on the devices and of the subscription descriptions.

Every device facility carries a short, stable *name* (the service, channel, spectrum or
pipe name a user typed) followed by where the other end is:

- ``"<name> > <far node> <far port>"`` on ports and facilities (:func:`device_label`);
- ``"<svc> via <ch1> + <ch2>"`` on cross-connects (:func:`via_label`);
- ``"<ch1> + <ch2>"`` on bundles of channels (:func:`conduits_label`).

The name always comes first, so the same token can be searched on the device and in the
orchestrator. Identifiers are never built here: the FlexILS OEL AID and ``CKTIDSUFFIX``
come from :mod:`orchestrator.optical.utils.identifiers`, the others are subscription
instance ids. Free-form descriptions never reach a device; they belong in the
subscription description only.

The FlexILS optical circuit objects carry what does not fit their short identifiers:

- ``"<spectrum name> <hop1><hop2>...<hopN>"`` on an OEL (:func:`oel_label`);
- ``"<svc1><svc2>... <hop1><hop2>...<hopN>"`` on an OSNC (:func:`osnc_label`);

the hops being the location codes of the nodes of the whole spectrum path, amplifiers
left out (:func:`path_location_codes`). Inside a group the tokens are joined without a
separator: a substring search finds them all the same and more of them fit.

When a label is longer than :data:`DEVICE_LABEL_MAX_LENGTH` the far-end part is dropped
first (a truncated port name would be misleading), then the name is cut.
"""

from collections.abc import Iterable, Sequence
from typing import Any, Final

__all__ = [
    "DEVICE_LABEL_MAX_LENGTH",
    "FLEXILS_CIRCUIT_LABEL_MAX_LENGTH",
    "conduits_label",
    "device_label",
    "endpoint",
    "label_name",
    "node_name",
    "oel_label",
    "osnc_label",
    "path_location_codes",
    "via_label",
]

#: Longest label written on a device. Not yet checked against every vendor reference:
#: lower it if a device rejects a label.
DEVICE_LABEL_MAX_LENGTH: Final = 64

#: Longest label of a FlexILS OEL or OSNC (tested on a node).
FLEXILS_CIRCUIT_LABEL_MAX_LENGTH: Final = 120

#: Role of the nodes left out of the hops of a path (``OpticalNodeRole.AMPLIFIER``).
_AMPLIFIER_ROLE: Final = "Amplifier"

#: Separates the name from the far end in a device label.
FAR_END_SEPARATOR: Final = " > "
#: Joins channel names in a bundle label.
CONDUIT_SEPARATOR: Final = " + "


def node_name(optical_node_block: Any) -> str:
    """Return the name a node is known by on the devices: the FlexILS TID, else the management name."""
    target_id = getattr(optical_node_block, "optical_flexils_target_id", None)
    if target_id:
        return str(target_id)
    name = optical_node_block.management.optical_module_node_name
    return str(name) if name else "<unknown>"


def endpoint(optical_node_block: Any, port_name: str | None) -> str:
    """Return ``"<node> <port>"``, the far end of a label or one side of a description."""
    if not port_name:
        return node_name(optical_node_block)
    return f"{node_name(optical_node_block)} {port_name}"


def _fit(full: str, short: str, max_length: int) -> str:
    if len(full) <= max_length:
        return full
    return short[:max_length]


def device_label(name: str | None, far_end: str | None = None, *, max_length: int = DEVICE_LABEL_MAX_LENGTH) -> str:
    """Return ``"<name> > <far end>"``, ``"> <far end>"`` without a name, or the name alone.

    Args:
        name: The user-facing name of what the facility carries (may be empty).
        far_end: Where the other end of the facility is, see :func:`endpoint`.
        max_length: Longest label the device accepts.

    Returns:
        The label; the far end is dropped first when it does not fit.
    """
    name = (name or "").strip()
    if not far_end:
        return name[:max_length]
    full = f"{name}{FAR_END_SEPARATOR}{far_end}" if name else f"{FAR_END_SEPARATOR.lstrip()}{far_end}"
    return _fit(full, name, max_length)


def label_name(label: str) -> str:
    """Return the name part of a label built by :func:`device_label`."""
    return label.partition(FAR_END_SEPARATOR)[0].strip()


def conduits_label(names: Iterable[str], *, max_length: int = DEVICE_LABEL_MAX_LENGTH) -> str:
    """Return ``"<ch1> + <ch2>"``: the names in order, without duplicates."""
    return CONDUIT_SEPARATOR.join(dict.fromkeys(name.strip() for name in names if name.strip()))[:max_length]


def via_label(name: str, conduits: Iterable[str], *, max_length: int = DEVICE_LABEL_MAX_LENGTH) -> str:
    """Return ``"<name> via <ch1> + <ch2>"``, or the name alone when it does not fit."""
    name = name.strip()
    channels = conduits_label(conduits, max_length=10 * max_length)
    if not channels:
        return name[:max_length]
    return _fit(f"{name} via {channels}", name, max_length)


def path_location_codes(sections: Sequence[Any]) -> list[str]:
    """Return the location codes of the nodes of a whole spectrum path, in path order.

    The path is every section's source add/drop port, express ports and destination
    add/drop port. Amplifier nodes are left out and consecutive ports at the same
    location count once.

    Args:
        sections: The Optical Spectrum Section blocks of the spectrum, in path order.

    Returns:
        The location codes: the first is the source of the path, the last its destination.
    """
    codes: list[str] = []
    for section in sections:
        source, destination = section.optical_spectrum_section_add_drop_ports
        for port in (source, *section.optical_spectrum_section_express_ports, destination):
            node = port.optical_port_host_node
            if str(getattr(node, "optical_node_role", "") or "") == _AMPLIFIER_ROLE:
                continue
            code = str(node.location.location_code)
            if not codes or codes[-1] != code:
                codes.append(code)
    return codes


def _grouped_label(head: str, hops: Iterable[str]) -> str:
    return f"{head} {''.join(hops)}".strip()[:FLEXILS_CIRCUIT_LABEL_MAX_LENGTH].rstrip()


def oel_label(spectrum_name: str, hops: Iterable[str]) -> str:
    """Return the OEL label ``"<spectrum name> <hop1><hop2>...<hopN>"``, cut from the right."""
    return _grouped_label(spectrum_name.strip(), hops)


def osnc_label(service_names: Iterable[str], hops: Iterable[str]) -> str:
    """Return the OSNC label ``"<svc1><svc2>... <hop1><hop2>...<hopN>"``, cut from the right.

    Args:
        service_names: Names of the digital services carried (none for a bare spectrum):
            written sorted, without duplicates.
        hops: Location codes of the nodes of the path, see :func:`path_location_codes`.

    Returns:
        The label; the hops alone when no service is carried.
    """
    services = "".join(sorted({name.strip() for name in service_names if name.strip()}))
    return _grouped_label(services, hops)
