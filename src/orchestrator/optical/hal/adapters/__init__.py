"""Per-device adapters for the optical HAL.

Each subpackage is one supported device (vendor + platform) and holds the
device-specific implementations of the area operations (``node``, ``port``,
``transponder``, ``spectrum``). A device only ships the area modules it
supports; the area dispatchers in :mod:`orchestrator.optical.hal` route to the
right adapter with ``match/case`` on the node's vendor and platform.

Device-level, cross-area helpers (client factory, port-name parsers, ...) live
in each device's ``_shared`` module.
"""
