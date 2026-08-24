"""Workflows for Optical Module Locations.

This package ships the ready-to-use ``create_optical_module_location``,
``modify_optical_module_location``, ``terminate_optical_module_location`` and
``validate_optical_module_location`` workflows of the shipped
``OpticalModuleLocationSubscription`` product type, together with the
importable parts: the FormPages of the shipped forms (as page sequences that
consumers yield from in one line, e.g. ``create_optical_module_location_form_pages``)
and the step lists that operate on the shipped ``OpticalModuleLocationBlock``
found in the state under ``OPTICAL_LOCATION_BLOCK_STATE_KEY``.
"""
