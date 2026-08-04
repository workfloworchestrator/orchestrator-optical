"""TNMS (Transport Network Management System) API Client Package.

This package provides a client interface for interacting with the TNMS API.
It handles authentication and provides methods for device management operations.

Example:
    >>> from orchestrator.optical.services.nokia import get_tnms_client
    >>> devices = get_tnms_client().data.equipment.devices.retrieve(fields=["name", "type"])

Note:
    The package is configured using the ``OPTICAL_TNMS_*`` settings (see
    :mod:`orchestrator.optical.settings`):

    - ``OPTICAL_TNMS_ENDPOINT`` (required)
    - ``OPTICAL_TNMS_USER`` (required)
    - ``OPTICAL_TNMS_PASSWORD`` (required)
    - ``OPTICAL_TNMS_SECONDARY_ENDPOINT`` (optional fallback endpoint)

    The client instance is created lazily on first use from the settings and raises
    :class:`ValidationError` when the required values are missing.
"""
