"""Pydantic custom type of the name of an Optical Node."""

from typing import Annotated

from pydantic import StringConstraints

#: Longest name accepted: the ``ne-name`` leaf of the NETCONF devices holds up to 256 characters.
OPTICAL_NODE_NAME_MAX_LENGTH = 256

#: Name of an Optical Node: the name the node is known by (by default the one read from the
#: device). It is free-form, case-preserving text; a fully qualified domain name is a valid
#: name but is not required.
OpticalNodeName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=OPTICAL_NODE_NAME_MAX_LENGTH),
]
