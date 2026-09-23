"""Workflows for Optical Fiber Patches.

This package ships the ready-to-use ``create_fiber_patch``,
``modify_fiber_patch``, ``terminate_fiber_patch``, ``validate_fiber_patch`` and
``reconcile_fiber_patch``
workflows of the shipped ``OpticalFiberPatch`` product type, together with the
importable parts: the FormPages of the shipped forms (as page sequences that
consumers yield from in one line, e.g. ``create_fiber_patch_form_pages``) and
the step lists that operate on the shipped ``OpticalFiberPatchBlock`` found in
the state under ``OPTICAL_MODULE_BLOCK_STATE_KEY``.
"""
