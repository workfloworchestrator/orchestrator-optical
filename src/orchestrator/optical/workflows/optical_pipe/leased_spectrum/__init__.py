"""Workflows for Optical Leased Spectrum pipes.

This package ships the ready-to-use ``create_leased_spectrum``,
``modify_leased_spectrum``, ``terminate_leased_spectrum`` and
``validate_leased_spectrum`` workflows of the shipped ``OpticalLeasedSpectrum``
product type, together with the importable parts: the FormPages of the shipped
forms (as page sequences that consumers yield from in one line, e.g.
``create_leased_spectrum_form_pages``) and the step lists that operate on the
shipped ``OpticalLeasedSpectrumBlock`` found in the state under
``OPTICAL_PIPE_BLOCK_STATE_KEY``.
"""
