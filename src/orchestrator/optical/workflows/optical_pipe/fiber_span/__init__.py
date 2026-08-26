"""Workflows for Optical Fiber Spans.

This package ships the ready-to-use ``create_fiber_span``,
``modify_fiber_span``, ``terminate_fiber_span`` and ``validate_fiber_span``
workflows of the shipped ``OpticalFiberSpan`` product type, together with the
importable parts: the FormPages of the shipped forms (as page sequences that
consumers yield from in one line, e.g. ``create_fiber_span_form_pages``) and
the step lists that operate on the shipped ``OpticalFiberSpanBlock`` found in
the state under ``OPTICAL_PIPE_BLOCK_STATE_KEY``.
"""
